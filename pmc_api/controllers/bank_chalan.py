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


class BankChalanPDFView(APIView):
    def get(self, request, *args, **kwargs):
        applicant_id = request.GET.get("ApplicantId", 3)
        if not applicant_id:
            raise NotFound("ApplicantId parameter is required.")

        # Fetch the applicant details
        applicant = get_object_or_404(ApplicantDetail, id=applicant_id)

        # Fetch related business profile
        business_profile = getattr(applicant, 'businessprofile', None)

        # Fetch producer details if available
        producer = Producer.objects.filter(applicant=applicant).first()

        # Determine fee
        license_type = applicant.registration_for
        fee = None
        if license_type == 'Producer' and producer:
            if producer.number_of_machines:
                machines = int(producer.number_of_machines)
                if machines <= 5:
                    fee = fee_structure['Producer']['upto_5_machines']
                elif 6 <= machines <= 10:
                    fee = fee_structure['Producer']['from_6_to_10_machines']
                else:
                    fee = fee_structure['Producer']['more_than_10_machines']
        elif license_type in fee_structure:
            entity_type = business_profile.entity_type if business_profile else "Individual"
            fee = fee_structure[license_type].get(entity_type, 0)  # Default to 0 if no match found

        # Check if fee already exists
        existing_fee = ApplicantFee.objects.filter(applicant=applicant, fee_amount=fee).first()
        if not existing_fee:
            # Save new fee
            ApplicantFee.objects.create(applicant=applicant, fee_amount=fee, is_settled=False)
            
        # Format data for the template
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M")

        # Generate QR Code with applicant_id and tracking_hash
        url = f"https://plmis.epapunjab.pk?applicant_id={applicant.id}&tracking_hash={applicant.tracking_hash}"
        qr_code_image = generate_qr_code(url)
        base64_qr = base64.b64encode(qr_code_image.read()).decode()
        nbp_charges = 0
        amount_total = fee + nbp_charges
        # Convert fee to words
        fee_in_words = f"{num2words(amount_total)} rupees only." if amount_total else "N/A"

        # Prepare data for the receipt
        data = {
            'applicant_name': f"{applicant.first_name} {applicant.last_name or ''}",
            'qr_code': f"data:image/png;base64,{base64_qr}",
            'application_date': formatted_datetime,
            'business_name': f"{business_profile.name or ''} {applicant.tracking_number}" if business_profile else "N/A",
            'amount': f"Rs. {fee:,}" if fee else "N/A",
            'amount_total': f"Rs. {amount_total:,}" if amount_total else "N/A",
            'amount_words': fee_in_words,
            "license_code": applicant.tracking_number,
            "nbp_charges": nbp_charges
        }

        # Render HTML from a Django template
        html = render_to_string('chalan.html', data)
        options = {
            'page-size': 'a4',
            'encoding': 'UTF-8',
            'margin-top': '2mm',
            'margin-right': '2mm',
            'margin-bottom': '2mm',
            'margin-left': '2mm',
        }
        pdf = pdfkit.from_string(html, False, options=options)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="out.pdf"'
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

class PingView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'status': 'verified', 'message': 'verified.'}, status=status.HTTP_200_OK)


class VerifyChalanQRCodeView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):

        return Response({'status': 'verified', 'message': 'QR code is valid.'}, status=status.HTTP_200_OK)
        """
        applicant_id_param = request.POST.get("ApplicantId", 3)
        if not applicant_id_param:
            raise NotFound("ApplicantId parameter is required.")

        # Extract the uploaded file
        uploaded_file = request.FILES.get('chalan_image')
        if not uploaded_file:
            return Response({'error': 'No file uploaded.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Open the image using Pillow
            image = Image.open(uploaded_file)

            # Decode the QR code from the image
            decoded_objects = decode(image)

            if not decoded_objects:
                return Response({'error': 'No QR code found in the image.'}, status=status.HTTP_400_BAD_REQUEST)

            # Extract the data from the QR code
            qr_data = decoded_objects[0].data.decode('utf-8')  # Assuming the first QR code is the one we need

            # Parse URL parameters
            from urllib.parse import urlparse, parse_qs
            parsed_url = urlparse(qr_data)
            query_params = parse_qs(parsed_url.query)

            applicant_id = query_params.get('applicant_id', [None])[0]
            p_tracking_hash = query_params.get('tracking_hash', [None])[0]

            if not applicant_id or not p_tracking_hash:
                return Response({'status': 'invalid', 'message': 'QR code data is incomplete.'},
                                status=status.HTTP_400_BAD_REQUEST)
            print(applicant_id_param)
            print(applicant_id)
            if applicant_id != applicant_id_param:
                return Response(
                    {'status': 'invalid', 'message': 'Uploaded Challan is not generated for current application.'},
                    status=status.HTTP_400_BAD_REQUEST)

            # Validate against the database
            applicant = get_object_or_404(
                ApplicantDetail,
                id=applicant_id,
                tracking_hash=p_tracking_hash,
                created_by=request.user.id  # Ensure created_by matches the signed-in user
            )

            # If applicant is found and matches criteria, return verified response
            return Response({'status': 'verified', 'message': 'QR code is valid.'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': f'Error processing image: {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        """