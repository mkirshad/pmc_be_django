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
from pmc_api.models import *
from pmc_api.models_choices import fee_structure
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication

class ApplicationReceiptPDFView(APIView):
    authentication_classes = [JWTAuthentication]  # Allow Bearer token authentication
    permission_classes = [AllowAny]  # Allow public access, filter logic will restrict records
    print('its in begining at 2 lines')
    def get(self, request, *args, **kwargs):
        applicant_id = request.GET.get("ApplicantId")
        tracking_hash = request.GET.get("TrackingHash", None)
        print('its in begining at 4 lines')
        if not applicant_id:
            raise NotFound("ApplicantId parameter is required.")

        # If user is authenticated, filter applicants based on created_by
        if request.user.is_authenticated:
            applicant = get_object_or_404(ApplicantDetail, id=applicant_id, created_by=request.user.id)
        else:
            # If user is not authenticated, fetch the applicant without restriction
            applicant = get_object_or_404(ApplicantDetail, id=applicant_id, tracking_hash=tracking_hash)

        # Fetch related business profile
        business_profile = getattr(applicant, 'businessprofile', None)

        if business_profile:
            print(f"BusinessProfile exists: {business_profile}")
            print(f"BusinessProfile name: {business_profile.name}")
        else:
            print("BusinessProfile does not exist for this ApplicantDetail.")

        license_type = applicant.registration_for

        # Format data for the template
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%d %B %Y, %I:%M %p")

        # Generate QR Code
        url_base = request.build_absolute_uri()
        url = f"{url_base}&TrackingHash={str(applicant.tracking_hash)}"
        print('its going to start qr code')
        #url = request.GET.get("url", "https://plmis.epapunjab.pk/api/pmc/receipt-pdf?ApplicantId="+str(applicant_id)+"&TrackingHash="+str(applicant.tracking_hash))
        qr_code_image = generate_qr_code(url)
        base64_qr = base64.b64encode(qr_code_image.read()).decode()
        print('end QR Code')
        # Prepare data for the receipt
        data = {
            'applicant_no': applicant.tracking_number,
            'qr_code': f"data:image/png;base64,{base64_qr}",
            'applicant_name': f"{applicant.first_name} {applicant.last_name or ''}",
            'application_date': formatted_datetime,
            'business_name': business_profile.name if business_profile else "N/A",
            'license_type': license_type or "N/A",
            'business_address': business_profile.postal_address if business_profile else "N/A",
        }

        # Render the receipt template
        


        # url = request.GET.get("url", "https://epd.punjab.gov.pk/epa_directorate")
        # qr_code_image = generate_qr_code(url)
        # Convert the QR code image to base64
        # base64_qr = base64.b64encode(qr_code_image.read()).decode()
        # current_datetime = datetime.now()
        # formatted_datetime = current_datetime.strftime("%d %B %Y, %I:%M %p")
        # formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M")
        # template = get_template('receipt.html')
        print('Generating PDF')
        # Render HTML from a Django template
        html = render_to_string('receipt.html', data)
        # Generate PDF from the rendered HTML
        pdf = pdfkit.from_string(html, False)
        print('pdf created')
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Receipt-'+str(applicant_id)+'.pdf"'
        return response


def generate_qr_code(url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=20,
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
