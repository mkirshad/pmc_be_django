import json
import re

import requests
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from oauth2_provider.views import TokenView
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status, serializers
from datetime import datetime, timedelta
from rest_framework.views import APIView
from pmc_api.controllers.CustomTokenAuthentication import CustomTokenAuthentication
from pmc_api.models import *
from django.contrib.auth.decorators import login_required
from requests.exceptions import RequestException
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
from django.template.loader import render_to_string, get_template

@api_view(['POST'])
@authentication_classes([])  # Disable authentication
@permission_classes([])
def plmis_token_view(request):
    """
    Custom endpoint for obtaining access tokens.
    """
    try:
        client_id = request.data.get('clientId', None)
        client_secret = request.data.get('clientSecretKey', None)
        grant_type = request.data.get('grant_type', 'client_credentials')
        request._request.POST = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': grant_type,
        }
        token_view = TokenView.as_view()
        response = token_view(request._request)
        # Parse the JSON data from response.content
        response_data = json.loads(response.content)
        status_text = "OK"
        if 'error' in response_data:
            status_text = "Fail"
        # Extract the access token and other information
        access_token = response_data.get("access_token", "")
        token_type = response_data.get("token_type", "")
        expires_in = response_data.get("expires_in", 0)

        # Calculate the expiry date
        expiry_date = timezone.localtime() + timedelta(seconds=expires_in)
        expiry_date_str = expiry_date.strftime('%Y-%m-%d %H:%M:%S')

        # Prepare the custom response
        custom_response = {
            "status": status_text,
            "message": "",
            "content": [
                {
                    "clientId": client_id,  # Use the client ID from the request
                    "token": {
                        "tokenType": token_type,
                        "accessToken": access_token,
                    },
                    "expiryDate": expiry_date_str,
                }
            ]
        }
        return Response(custom_response)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


def get_or_refresh_token(service_name, auth_endpoint, client_id, client_secret):
    """
    Expects a response of the form:
    {
      "status": "OK",
      "content": [
        {
          "token": {
            "tokenType": "Bearer",
            "accessToken": "<YOUR_JWT>"
          },
          "clientId": "asrELpn41!T",
          "expiryDate": 1736345356000
        }
      ],
      "message": null
    }
    """
    # 1. Try to get the existing token
    token_obj = ExternalServiceToken.objects.filter(
        service_name=service_name
    ).order_by("-created_at").first()

    # 2. If no token in DB or it's expired, request a new one
    if not token_obj or token_obj.is_expired():
        payload = {
            "clientId": client_id,
            "clientSecretKey": client_secret
        }

        # Make the request
        try:
            resp = requests.post(auth_endpoint, json=payload)
        except RequestException as req_err:
            # Create a pseudo-response dict if a network error occurs
            resp = {
                "error": "Request to auth endpoint failed",
                "details": str(req_err),
                "status_code": 0
            }

        # Attempt to parse JSON if we got an actual response object
        try:
            data = resp.json() if isinstance(resp, requests.Response) else resp
        except Exception:
            data = resp

        # Log the request/response to ApiLog
        ApiLog.objects.create(
            service_name=service_name,
            endpoint=auth_endpoint,
            request_data=payload,
            response_data=data,
            status_code=getattr(resp, "status_code", 0)  # fallback to 0 if not a real response
        )

        # Parse the new structure:
        #
        #   data["content"][0]["token"]["accessToken"]
        #   data["content"][0]["expiryDate"]   (epoch milliseconds)
        #
        # Safely navigate the keys:
        content_list = data.get("content", [])
        if content_list:
            first_item = content_list[0]
            token_info = first_item.get("token", {})
            new_token = token_info.get("accessToken", "")
            expiry_ms = first_item.get("expiryDate", 0)
        else:
            # Fallback if content is missing
            new_token = ""
            expiry_ms = 0

        # Convert epoch milliseconds -> datetime, or fallback to +1 hour if missing
        if expiry_ms > 0:
            # epoch ms -> seconds -> datetime
            expiry_dt = datetime.fromtimestamp(expiry_ms / 1000.0)
        else:
            expiry_dt = datetime.now() + timedelta(seconds=3600)

        # Create a new token object in DB
        token_obj = ExternalServiceToken.objects.create(
            access_token=new_token,
            expires_at=expiry_dt,
            service_name=service_name
        )

    # 3. Return the token
    return token_obj.access_token

@api_view(['POST'])
@authentication_classes([CustomTokenAuthentication])
@permission_classes([AllowAny])
def payment_intimation_view(request):
    """
    API view for processing payment intimations with detailed validation.
    """
    data = request.data
    required_fields = ['consumerNumber', 'psidStatus', 'deptTransactionId', 'amountPaid', 'paidDate', 'paidTime', 'bankCode']

    # Validate required fields
    for field in required_fields:
        if not data.get(field):
            response_data = {"status": "Fail", "message": f"{field} is required and cannot be empty"}
            return log_and_respond(request, response_data, status.HTTP_400_BAD_REQUEST)

    # Validate consumerNumber
    consumer_number = data.get('consumerNumber')
    if not consumer_number or len(consumer_number.strip()) == 0:
        response_data = {"status": "Fail", "message": "Consumer number cannot be empty or invalid"}
        return log_and_respond(request, response_data, status.HTTP_400_BAD_REQUEST)

    # Validate deptTransactionId
    dept_transaction_id = data.get('deptTransactionId')
    if not dept_transaction_id or len(dept_transaction_id.strip()) == 0:
        response_data = {"status": "Fail", "message": "Department transaction ID/Challan number cannot be empty"}
        return log_and_respond(request, response_data, status.HTTP_400_BAD_REQUEST)

    # Validate psidStatus
    psid_status = data.get('psidStatus')
    if psid_status != "PAID":
        response_data = {"status": "Fail", "message": "PSID status must be 'PAID'"}
        return log_and_respond(request, response_data, status.HTTP_400_BAD_REQUEST)

    # Validate paidDate
    try:
        paid_date = datetime.strptime(data['paidDate'], '%Y-%m-%d').date()
    except ValueError:
        response_data = {"status": "Fail", "message": "Paid date must be in YYYY-MM-DD format"}
        return log_and_respond(request, response_data, status.HTTP_400_BAD_REQUEST)

    # Validate paidTime
    try:
        paid_time = datetime.strptime(data['paidTime'], '%H:%M:%S').time()
    except ValueError:
        response_data = {"status": "Fail", "message": "Paid time must be in HH:MM:SS format"}
        return log_and_respond(request, response_data, status.HTTP_400_BAD_REQUEST)

    # Validate amountPaid
    try:
        amount_paid = float(data['amountPaid'])
        if amount_paid <= 0:
            raise ValueError
    except ValueError:
        response_data = {"status": "Fail", "message": "Amount paid must be a positive number"}
        return log_and_respond(request, response_data, status.HTTP_400_BAD_REQUEST)

    # Validate Bank Code
    bank_code = data['bankCode']
    if not bank_code.isalnum():
        response_data = {"status": "Fail", "message": "Bank code cannot contain special characters"}
        return log_and_respond(request, response_data, status.HTTP_400_BAD_REQUEST)

    # Fetch the PSIDTracking record
    psid_record = PSIDTracking.objects.filter(
        consumer_number=consumer_number,
        dept_transaction_id=dept_transaction_id
    ).order_by('-created_at').first()

    if not psid_record:
        response_data = {"status": "Fail", "message": "No matching PSID record found for the provided consumer number and challan number"}
        return log_and_respond(request, response_data, status.HTTP_400_BAD_REQUEST)

    # Check if already paid
    if psid_record.payment_status == "PAID":
        response_data = {"status": "OK", "message": "PSID is already marked as PAID"}
        return log_and_respond(request, response_data, status.HTTP_200_OK)

    # Validate amount matches
    if psid_record.amount_within_due_date != amount_paid:
        response_data = {"status": "Fail", "message": "Amount paid does not match the expected amount"}
        return log_and_respond(request, response_data, status.HTTP_400_BAD_REQUEST)

    # Update PSIDTracking record
    psid_record.payment_status = psid_status
    psid_record.amount_paid = amount_paid
    psid_record.paid_date = paid_date
    psid_record.paid_time = paid_time
    psid_record.bank_code = bank_code
    psid_record.message = "Payment intimated successfully"

    if psid_record.applicant:
        applicant = psid_record.applicant
        applicant.application_status = 'Submitted'
        applicant.save()

    psid_record.save()

    # Successful response
    response_data = {"status": "OK", "message": "Payment intimated successfully"}
    return log_and_respond(request, response_data, status.HTTP_200_OK)


def log_and_respond(request, response_data, status_code):
    """
    Helper function to log the API response and return a response.
    """
    ApiLog.objects.create(
        service_name="payment_intimation_exposed",
        endpoint=request.build_absolute_uri(),
        request_data=request.data,
        response_data=response_data,
        status_code=status_code
    )
    return Response(response_data, status=status_code)



class CheckPSIDPaymentStatus(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        applicant_id = request.GET.get("applicant_id")
        user = request.user

        if not applicant_id:
            return JsonResponse({"status": "error", "message": "Missing applicant_id"}, status=400)

        # Fetch the applicant and the latest PSIDTracking record
        applicant = get_object_or_404(ApplicantDetail, id=applicant_id, created_by=user)
        psid_record = PSIDTracking.objects.filter(applicant=applicant).order_by('-created_at').first()

        if not psid_record or not psid_record.consumer_number:
            return JsonResponse({"status": "error", "message": "No PSID found for the applicant"}, status=404)

        # Prepare the payload for the API
        payload = {"consumerNumber": psid_record.consumer_number}

        config = ServiceConfiguration.objects.get(service_name="ePay")
        token = get_or_refresh_token(
            service_name=config.service_name,
            auth_endpoint=config.auth_endpoint,
            client_id=config.client_id,
            client_secret=config.client_secret
        )
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # 7. Call ePay
        try:
            response = requests.post(config.transaction_status_endpoint, json=payload, headers=headers)
            status_code = response.status_code
        except RequestException as req_err:
            status_code = 0
            response = {
                "error": "Request to generate_psid_endpoint failed",
                "details": str(req_err),
            }

        if isinstance(response, requests.Response):
            try:
                response_data = response.json()
            except Exception:
                response_data = {
                    "error": "Could not parse JSON from generate_psid_endpoint",
                    "body": response.text
                }
        else:
            response_data = response

        # 8. Log the API call
        ApiLog.objects.create(
            service_name=config.service_name,
            endpoint=config.generate_psid_endpoint,
            request_data=payload,
            response_data=response_data,
            status_code=status_code
        )

        if response.status_code == 200 and response_data.get("status") == "OK":
            content = response_data.get("content", [{}])[0]
            psid_status = content.get("psidStatus", "UNPAID")
            amount_paid = content.get("amountPaid", None)
            paid_date = content.get("paidDate", None)
            paid_time = content.get("paidTime", None)
            bank_code = content.get("bankCode", None)

            # Update the PSIDTracking record
            psid_record.payment_status = psid_status
            if psid_status == "PAID":
                psid_record.amount_paid = amount_paid
                psid_record.paid_date = paid_date
                psid_record.paid_time = paid_time
                psid_record.bank_code = bank_code
            psid_record.save()

            # Return payment status as JSON
            return JsonResponse({
                "status": "success",
                "psid_status": psid_status,
                "amount_paid": amount_paid,
                "paid_date": paid_date,
                "paid_time": paid_time,
                "bank_code": bank_code,
                "message": response_data.get("message", ""),
            }, status=200)
        else:
            return JsonResponse({
                "status": "error",
                "message": response_data.get("message", "Unable to fetch payment status"),
                "details": response_data
            }, status=response.status_code)

class GeneratePsid(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # 1. Retrieve applicant_id from request (e.g., ?applicant_id=123)
        GRACE_PRIOD_DAYS = 15
        applicant_id = request.GET.get("applicant_id")
        user = request.user
        if not applicant_id:
            return self._build_html_response(
                title="Error",
                body="<p>Missing applicant_id</p>",
                status_code=400
            )

        # 2. Fetch the applicant (ensuring created_by=user)
        applicant = get_object_or_404(ApplicantDetail, id=applicant_id, created_by=user, application_status__in=['Created', 'Fee Challan'])

        # -- Check if there's already a non-expired PSIDTracking --
        existing_psid_record = PSIDTracking.objects.filter(
            applicant=applicant,
            consumer_number__isnull=False  # Must have a PSID
        ).order_by('-id').first()

        # If we found an existing record, and it hasn't expired
        if existing_psid_record:
            if existing_psid_record.expiry_date >= timezone.localtime():
                # Build an HTML snippet showing the existing PSID

                data_view = {
                    'consumer_number': existing_psid_record.consumer_number,
                    'applicant_name': f"""{applicant.first_name} {applicant.last_name or ''}""",
                    'tracking_number': applicant.tracking_number,
                    'amount_within_due_date':existing_psid_record.amount_within_due_date,
                    'due_date':existing_psid_record.due_date,
                    'expiry_date':timezone.localtime(existing_psid_record.expiry_date)
                }
                html_content = render_to_string('receipt_psid.html', data_view)
                return HttpResponse(html_content, content_type="text/html")

        # == If we are here, either no record or it's expired, so generate a new one. ==

        # 3. Determine fee (same logic as before)
        business_profile = getattr(applicant, 'businessprofile', None)
        producer = Producer.objects.filter(applicant=applicant).first()

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
            fee = fee_structure[license_type].get(entity_type, 0)

        # 4. Check if an ApplicantFee already exists; if not, create one
        existing_fee = ApplicantFee.objects.filter(applicant=applicant, fee_amount=fee).order_by('-id').first()
        if not existing_fee:
            ApplicantFee.objects.create(applicant=applicant, fee_amount=fee, is_settled=False)

        last_fee_obj = ApplicantFee.objects.filter(applicant=applicant).order_by('-id').first()
        if not last_fee_obj:
            return self._build_html_response(
                title="Error",
                body="<p>No fee record found for this applicant.</p>",
                status_code=400
            )

        # deptTransactionId from applicant.tracking_number + "-" + last_fee_obj.id
        dept_transaction_id = f"{last_fee_obj.id}"

        # 5. Calculate dueDate (today) and expiryDate (15 days from now)
        due_date = (timezone.localtime() + timedelta(days=GRACE_PRIOD_DAYS)).date()
        expiry_datetime = (timezone.localtime() + timedelta(days=GRACE_PRIOD_DAYS)).replace(hour=23, minute=59, second=59, microsecond=0)
        expiry_str = expiry_datetime.strftime("%Y-%m-%d %H:%M:%S")

        fee_amount = last_fee_obj.fee_amount
        consumer_name = f"{applicant.first_name} {applicant.last_name or ''}".strip()
        # Prepend '0' to applicant.mobile_no
        full_mobile = f"0{applicant.mobile_no}"
        # Remove dashes from CNIC
        cnic_value = applicant.cnic.replace("-", "")

        district_id_val = 0
        if business_profile and business_profile.district:
            district_id_val = business_profile.district.pitb_district_id or 0

        applicant_email = applicant.email or f"{cnic_value}@cnic.pk"

        # 6. Prepare ePay config & token
        config = ServiceConfiguration.objects.get(service_name="ePay")
        token = get_or_refresh_token(
            service_name=config.service_name,
            auth_endpoint=config.auth_endpoint,
            client_id=config.client_id,
            client_secret=config.client_secret
        )

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        payload = {
            "deptTransactionId": dept_transaction_id,
            "dueDate": str(due_date),
            "expiryDate": expiry_str,
            "amountWithinDueDate": str(fee_amount),
            "amountAfterDueDate": "",
            "consumerName": consumer_name,
            "mobileNo": full_mobile,
            "cnic": cnic_value,
            "districtID": str(district_id_val),
            "email": applicant_email,
            "amountBifurcation": [
                {
                    "accountHeadName": "Initial Environmental Examination and Environmental Impact Assessment Review Fee",
                    "accountNumber": "C03855",
                    "amountToTransfer": str(fee_amount)
                }
            ]
        }

        # 7. Call ePay
        try:
            resp = requests.post(config.generate_psid_endpoint, json=payload, headers=headers)
            status_code = resp.status_code
        except RequestException as req_err:
            status_code = 0
            resp = {
                "error": "Request to generate_psid_endpoint failed",
                "details": str(req_err),
            }

        if isinstance(resp, requests.Response):
            try:
                response_data = resp.json()
            except Exception:
                response_data = {
                    "error": "Could not parse JSON from generate_psid_endpoint",
                    "body": resp.text
                }
        else:
            response_data = resp

        # 8. Log the API call
        ApiLog.objects.create(
            service_name=config.service_name,
            endpoint=config.generate_psid_endpoint,
            request_data=payload,
            response_data=response_data,
            status_code=status_code
        )

        # 9. If success, create new PSIDTracking and return HTML
        if status_code == 200 and response_data.get("status") == "OK":
            content_list = response_data.get("content", [])
            if content_list:
                consumer_number = content_list[0].get("consumerNumber", "")
                psid_record = PSIDTracking.objects.create(
                    applicant=applicant,
                    dept_transaction_id=dept_transaction_id,
                    due_date=due_date,
                    expiry_date=expiry_datetime,
                    amount_within_due_date=fee_amount,
                    amount_after_due_date=0,
                    consumer_name=consumer_name,
                    mobile_no=full_mobile,
                    cnic=cnic_value,
                    email=applicant_email,
                    district_id=district_id_val,
                    amount_bifurcation=payload["amountBifurcation"],
                    consumer_number=consumer_number,
                    status="OK",
                    message=response_data.get("message", "PSID generated successfully")
                )
                
                # Update the application_status to 'Fee Challan'
                applicant.application_status = 'Fee Challan'
                applicant.save()

                data_view = {
                    'consumer_number': consumer_number,
                    'applicant_name': f"""{applicant.first_name} {applicant.last_name or ''}""",
                    'tracking_number': applicant.tracking_number,
                    'amount_within_due_date':fee_amount,
                    'due_date':psid_record.due_date,
                    'expiry_date':timezone.localtime(psid_record.expiry_date)
                }
                html_content = render_to_string('receipt_psid.html', data_view)
                return HttpResponse(html_content, content_type="text/html")

            else:
                # No consumerNumber found in response
                fail_html = """
                <html>
                  <head><title>PSID Generation Failed</title></head>
                  <body>
                    <h1>PSID Generation Failed</h1>
                    <p>No consumerNumber found in the response content.</p>
                  </body>
                </html>
                """
                return HttpResponse(fail_html, content_type="text/html", status=400)
        else:
            # Not a 200 or no "OK" status in response
            fail_html = f"""
            <html>
              <head><title>PSID Generation Failed</title></head>
              <body>
                <h1>PSID Generation Failed</h1>
                <p>ePay returned an error or invalid status.</p>
                <pre>{response_data}</pre>
              </body>
            </html>
            """
            return HttpResponse(fail_html, content_type="text/html", status=400)

    def _build_html_response(self, title, body, status_code=200):
        """Utility method to quickly build an HTML response."""
        html = f"""
        <html>
          <head><title>{title}</title></head>
          <body>
            <h1>{title}</h1>
            {body}
          </body>
        </html>
        """
        return HttpResponse(html, content_type="text/html", status=status_code)
