import base64
from datetime import datetime

from django.http import HttpResponse
from django.template.loader import render_to_string, get_template
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView
import pdfkit
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
# from pyzbar.pyzbar import decode
from PIL import Image
from io import BytesIO
from pmc_api.models import *
from pmc_api.models_choices import fee_structure
from django.shortcuts import get_object_or_404
from num2words import num2words
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
from reportlab.lib.utils import ImageReader
from rest_framework import viewsets, permissions
from pmc_api.serializers import *
from pmc_api.threadlocals import get_current_user

def log_access(request, model_name, object_id):
    AccessLog.objects.create(
        user=get_current_user(),
        model_name=model_name,
        object_id=str(object_id),
        method=request.method,
        ip_address=request.META.get('REMOTE_ADDR'),
        endpoint=request.path
    )

# class LicensePDFView(APIView):
#     permission_classes = []
#     def get(self, request, *args, **kwargs):
#         # applicant_id = request.GET.get("ApplicantId", 3)
#         # if not applicant_id:
#         #     raise NotFound("ApplicantId parameter is required.")

#         # # Fetch the applicant details
#         # applicant = get_object_or_404(ApplicantDetail, id=applicant_id)

#         # # Fetch related business profile
#         # business_profile = getattr(applicant, 'businessprofile', None)

#         # # Fetch producer details if available
#         # producer = Producer.objects.filter(applicant=applicant).first()

#         # # Determine fee
#         # license_type = applicant.registration_for
        

#         # Render HTML from a Django template
#         data = {}
#         html = render_to_string('license.html', data)
#         options = {
#             'page-size': 'a4',
#             'orientation': 'landscape',  # Set the page orientation to landscape
#             'encoding': 'UTF-8',
#             'margin-top': '2mm',
#             'margin-right': '2mm',
#             'margin-bottom': '2mm',
#             'margin-left': '2mm',
#             'no-images': ''  # Skip loading images
#         }
#         pdf = pdfkit.from_string(html, False, options=options)
#         response = HttpResponse(pdf, content_type='application/pdf')
#         response['Content-Disposition'] = 'attachment; filename="out.pdf"'
#         return response








class LicensePDFView(APIView):
    permission_classes = []
    def get(self, request, *args, **kwargs):
        """
        1) Reads an existing 'template.pdf'
        2) Creates a new PDF overlay with absolute-positioned text using reportlab
        3) Merges overlay onto the template PDF using PyPDF2
        4) Returns the final stamped PDF
        """
        # 1) Read query parameters
        MAX_CHARACTERS = 66
        license_number = request.GET.get('license_number')
        date_of_issue = request.GET.get('date_of_issue')

        if not license_number:
            return HttpResponse("Missing license_number query parameter.", status=400)

        log_access(request, 'License', license_number)

        try:
            if date_of_issue:
                # Use provided date
                license_obj = License.objects.get(
                    license_number=license_number,
                    date_of_issue=date_of_issue,
                    is_active=True
                )
            else:
                # Fallback to latest license by issue date
                license_obj = License.objects.filter(
                    license_number=license_number,
                    is_active=True
                ).order_by('-date_of_issue').first()
                if not license_obj:
                    return HttpResponse("No active license found with the given license_number.", status=404)
        except License.DoesNotExist:
            return HttpResponse("No license found with the given license_number and date_of_issue.", status=404)


        # 3) Lookup district, tehsil from the applicant's businessprofile (if it exists)
        #    Because License has an integer applicant_id, we get that applicant record
        applicant = ApplicantDetail.objects.filter(id=license_obj.applicant_id).first()

        district_name = ""
        tehsil_name = ""
        if applicant and hasattr(applicant, 'businessprofile') and applicant.businessprofile:
            bp = applicant.businessprofile
            if bp.district:
                district_name = bp.district.district_name or ""
            if bp.tehsil:
                tehsil_name = bp.tehsil.tehsil_name or ""

        # 4) Concatenate license_obj.address + district_name + tehsil_name
        #    (only if they’re not empty)
        full_address = license_obj.address.strip()
        if tehsil_name:
            if not full_address.endswith(tehsil_name.strip()):
                full_address += f", {tehsil_name}"
        if district_name and tehsil_name.strip() != district_name.strip():
           full_address += f", {district_name}"
        print(tehsil_name)
        print(district_name)
        """"
            If the entire full_address fits within MAX_CHARACTERS, just use it as full_address1 and make full_address2 empty (i.e., don’t split at all).

            If the substring ends exactly at a space (i.e., not in the middle of a word), don’t “walk back” to the preceding space—just accept the substring as-is, and let the remainder be full_address2.
        """
        max_length = MAX_CHARACTERS

        # 1) If the address is already within max_length, put everything into full_address1 and nothing into full_address2
        if len(full_address) <= max_length:
            full_address1 = full_address
            full_address2 = ""
        else:
            # We have more than max_length characters, so take the first chunk
            temp_full_address1 = full_address[:max_length]
            
            # If the last character of this chunk is a space, we are NOT in the middle of a word
            # so just accept this chunk as is (minus the trailing space, if you'd like).
            if temp_full_address1.endswith(" "):
                # Optionally strip trailing space for a cleaner line:
                full_address1 = temp_full_address1.rstrip()
                # The rest is everything after what we kept
                full_address2 = full_address[len(full_address1) + 1:]
                
            else:
                # We might be cutting in the middle of a word. Let's see if there's a space in that chunk.
                space_index = temp_full_address1.rfind(" ")
                if space_index != -1:
                    # That means we *did* find a space somewhere before the end — we can avoid splitting a word
                    # by cutting at that space.
                    full_address1 = temp_full_address1[:space_index]
                    # Everything after that space goes to the second line
                    full_address2 = full_address[space_index + 1:]
                else:
                    # There's no space at all in that chunk, so we have to cut in the middle of the word.
                    # We'll just keep the chunk as is.
                    full_address1 = temp_full_address1
                    full_address2 = full_address[max_length:]

        
        # Path to your existing PDF (could be in static folder or somewhere accessible)
        landscape_size = landscape(A4)  # (842, 595)
        page_width, page_height = landscape_size
        
        pdf_path = "media/template/license1.pdf"

        # Read entire PDF into memory
        with open(pdf_path, "rb") as f:
            pdf_data = f.read()
        existing_pdf = PdfReader(BytesIO(pdf_data))

        # Get page size from first page
        first_page = existing_pdf.pages[0]
        width = float(first_page.mediabox.width)
        height = float(first_page.mediabox.height)  + 6

        # Create overlay with the same size
        overlay_buffer = BytesIO()
        c = canvas.Canvas(overlay_buffer, pagesize=(width, height))

        c.setFont("Times-Bold", 14)
        # c.drawString(
        #     180, height - 190, 
        #     "Producer / Stockist/Distributor/Supplier / Recycler of Plastic/Single Use Plastic"
        # )

        c.drawCentredString((width+14) / 2, height - 190, license_obj.license_for_formatted())
        
        c.setFont("Times-Roman", 14)
        # Place text near top-left
        c.drawString(280, height - 294, license_obj.license_number) # +7
        c.drawString(280, height - 320, license_obj.license_duration)
        c.drawString(280, height - 346, (license_obj.owner_name if len(license_obj.business_name) < 10 else license_obj.business_name)[:MAX_CHARACTERS])
        
        # c.drawString(280, height - 372, license_obj.business_name[:MAX_CHARACTERS])
        c.drawString(280, height - 372, license_obj.types_of_plastics_truncated())
        c.drawString(280, height - 396, full_address1)
        c.drawString(280, height - 423, full_address2)
        
        
        c.setFont("Times-Roman", 12)
        c.drawString(169, height - 464, license_obj.formatted_date_of_issue())
        
        
        # --- 4) Generate and Draw the QR code ---
        # Let's assume you have the function generate_qr_code(url)
        url = request.build_absolute_uri()
        qr_buffer = generate_qr_code(url)  # Replace with your actual URL

        # Convert the QR BytesIO into a ReportLab-friendly image
        qr_image = ImageReader(qr_buffer)

        # Draw the QR at (700, height-303), sized 33×33
        c.drawImage(qr_image, 690, height - 388, width=100, height=100)
        
        c.save()
        
        overlay_buffer.seek(0)
        overlay_pdf = PdfReader(overlay_buffer)

        writer = PdfWriter()

        # Merge single overlay page on each base PDF page
        overlay_page = overlay_pdf.pages[0]
        for base_page in existing_pdf.pages:
            # Merge overlay on top
            base_page.merge_page(overlay_page)
            writer.add_page(base_page)

        final_buffer = BytesIO()
        writer.write(final_buffer)
        final_buffer.seek(0)

        response = HttpResponse(final_buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="license.pdf"'
        return response

def generate_qr_code(url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Create the image
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return ContentFile(buffer.getvalue(), name="qrcode.png")

class LicenseByUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Ensure only authenticated users can access this view

    def get(self, request, *args, **kwargs):
        # Get the logged-in user
        user = request.user
        # Check if user has at least one group
        if user.groups.exists():
            # If the user is in any group, return all licenses
            licenses = License.objects.all()
            # Serialize the licenses
            serializer = LicenseSerializer(licenses, many=True)

            # Return the response
            return Response(serializer.data)
        
        # Fetch ApplicantDetail objects created by the logged-in user
        applicants = ApplicantDetail.objects.filter(created_by=user#, licenses__is_active=True
                                                    )

        # Get licenses associated with those applicants
        licenses = License.objects.filter(applicant_id__in=applicants.values_list('id', flat=True))

        # Serialize the licenses
        serializer = LicenseSerializer(licenses, many=True)

        # Return the response
        return Response(serializer.data)