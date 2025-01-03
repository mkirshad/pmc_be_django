from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from .models import *
from .serializers import *
from rest_framework.decorators import action
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db.models import Count,  F, Func, IntegerField, Count

from django.http import HttpResponse, JsonResponse, FileResponse, Http404
from django.shortcuts import get_object_or_404
import pdfkit
from django.contrib.auth.decorators import login_required
from .custom_permissions import IsOwnerOrAdmin
from django.db.models import Q
from django.core.exceptions import ValidationError
import os

class ApplicantDetailViewSet(viewsets.ModelViewSet):
    queryset = ApplicantDetail.objects.all()

    serializer_class = ApplicantDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        """
        Optionally restricts the returned queryset to records created by the currently authenticated user.
        If all records should be accessible, remove this method.
        """
        user = self.request.user
        target_groups = {'LSO', 'LSM', 'DO', 'TL', 'MO', 'LSM2','DEO', 'Download License'}
        user_groups = set(user.groups.values_list('name', flat=True))
        matching_groups = user_groups.intersection(target_groups)
        print(matching_groups)
        # Allow 'Super' group to access all records
        if "Super" in user_groups:
            print("Super user matched - returning all records")
            queryset = super().get_queryset()

            # Filter by assigned_group
            assigned_group = self.request.query_params.get("assigned_group")
            if assigned_group:
                queryset = queryset.filter(assigned_group=assigned_group)

            # Filter by application_status
            application_status = self.request.query_params.get("application_status")
            if application_status:
                queryset = queryset.filter(application_status=application_status)

            return queryset

        
        
        # Check for LSO specific filtering
        if "LSO" in matching_groups and user.username.lower().startswith("lso."):
            print('LSO is matched')
            username = user.username.lower()  # Ensure case-insensitivity
            if username.startswith("lso."):
                try:
                    user_suffix = int(username.split(".")[1])  # Extract the numeric suffix
                except (IndexError, ValueError):
                    return ApplicantDetail.objects.none()  # Return empty queryset for invalid usernames

                # Fetch IDs matching the pattern based on user's suffix
                ids_to_include = ApplicationSubmitted.objects.annotate(
                    mod_index=(models.F("id") - user_suffix) % 3  # Calculate modulo based on user suffix
                ).filter(mod_index=0).values_list("applicant_id", flat=True)

                return ApplicantDetail.objects.filter(
                    assigned_group__in=["LSO", "APPLICANT"],
                    id__in=ids_to_include,
                )
            
        # Check for DO specific filtering
        elif "DO" in matching_groups and user.username.lower().startswith("do."):
            print('do is matched')
            username = user.username.lower()
            if username.startswith("do."):
                try:
                    district_code = username.split(".")[1].upper()  # Extract district code from username and convert to uppercase
                except IndexError:
                    return ApplicantDetail.objects.none()  # Return empty queryset for invalid usernames
                print('going to return DO records')
                return ApplicantDetail.objects.filter(
                    assigned_group="DO",
                    businessprofile__district__short_name=district_code  # Match district code
                )
        elif matching_groups:
            return ApplicantDetail.objects.filter(assigned_group__in=matching_groups)
        else:
            return ApplicantDetail.objects.filter(created_by=user)
  

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    

    def destroy(self, request, *args, **kwargs):
        """
        Restrict delete operation: only allow superusers to delete records.
        """
        applicant_detail = self.get_object()  # Get the object to be deleted

        # Check if the user is a superuser
        if not request.user.is_superuser:
            return Response(
                {'detail': 'You do not have permission to delete this record.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Proceed with the delete if the user is a superuser
        return super().destroy(request, *args, **kwargs)

    def perform_update(self, serializer):
        # Remove 'tracking_hash' from validated data if present
        print('its in update of applicantDetail')
        validated_data = serializer.validated_data
        validated_data.pop('tracking_hash', None)  # Prevent tracking_hash updates
        serializer.save()

class ApplicantDetailMainListViewSet(viewsets.ModelViewSet):
    queryset = ApplicantDetail.objects.all()

    serializer_class = ApplicantDetailMainListSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        """
        Optionally restricts the returned queryset to records created by the currently authenticated user.
        If all records should be accessible, remove this method.
        """
        user = self.request.user
        target_groups = {'LSO', 'LSM', 'DO', 'TL', 'MO', 'LSM2','DEO', 'Download License'}
        user_groups = set(user.groups.values_list('name', flat=True))
        matching_groups = user_groups.intersection(target_groups)
        print(matching_groups)
        # Allow 'Super' group to access all records
        if "Super" in user_groups:
            print("Super user matched - returning all records")
            queryset = super().get_queryset()

            # Filter by assigned_group
            assigned_group = self.request.query_params.get("assigned_group")
            if assigned_group:
                queryset = queryset.filter(assigned_group=assigned_group)

            # Filter by application_status
            application_status = self.request.query_params.get("application_status")
            if application_status:
                queryset = queryset.filter(application_status=application_status)

            return queryset

class ApplicantManualFieldsViewSet(viewsets.ModelViewSet):
    queryset = ApplicantManualFields.objects.all()
    serializer_class = ApplicantManualFieldsSerializer

class ApplicantFieldResponseViewSet(viewsets.ModelViewSet):
    queryset = ApplicantFieldResponse.objects.all()
    serializer_class = ApplicantFieldResponseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Check if the request data is a list
        is_bulk = isinstance(request.data, list)

        if is_bulk:
            # Use many=True to handle bulk data
            serializer = self.get_serializer(data=request.data, many=True)
        else:
            serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        # Save data with the current user
        if is_bulk:
            serializer.save(created_by=self.request.user)
        else:
            serializer.save(created_by=self.request.user)

        # Return the appropriate response
        if is_bulk:
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        # Ensure created_by is always set
        serializer.save(created_by=self.request.user)

class BusinessProfileViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing, creating, updating, and deleting BusinessProfile records.
    """
    serializer_class = BusinessProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        """
        Returns BusinessProfile instances associated with the authenticated user.
        """
        return BusinessProfile.objects.all()  # Replace with filtering logic if needed

    def perform_create(self, serializer):
        """
        Automatically set updated_by during creation.
        """
        serializer.save(updated_by=self.request.user)
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        """
        Automatically update updated_by when a record is updated.
        """
        serializer.save(updated_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        """
        Custom delete behavior, if needed.
        """
        instance = self.get_object()
        if not request.user.is_superuser:
            return Response(
                {'detail': 'Only superusers can delete this record.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def by_applicant(self, request):
        applicant_id = request.query_params.get('applicant_id')
        if applicant_id:
            profiles = self.get_queryset().filter(applicant_id=applicant_id)
            serializer = self.get_serializer(profiles, many=True)
            return Response(serializer.data)
        return Response({'error': 'applicant_id is required'}, status=400)


class PlasticItemsViewSet(viewsets.ModelViewSet):
    queryset = PlasticItems.objects.all()
    serializer_class = PlasticItemsSerializer
    permission_classes = [permissions.IsAuthenticated]


class ProductsViewSet(viewsets.ModelViewSet):
    queryset = Products.objects.all()
    serializer_class = ProductsSerializer
    permission_classes = [permissions.IsAuthenticated]


class ByProductsViewSet(viewsets.ModelViewSet):
    queryset = ByProducts.objects.all()
    serializer_class = ByProductsSerializer
    permission_classes = [permissions.IsAuthenticated]


class ProducerViewSet(viewsets.ModelViewSet):
    queryset = Producer.objects.all()
    serializer_class = ProducerSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def create(self, request, *args, **kwargs):
        applicant_id = request.data.get('applicant')

        if not applicant_id:
            return Response({"error": "Applicant is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if a Producer already exists for this applicant
        try:
            producer = Producer.objects.get(applicant_id=applicant_id, created_by=self.request.user.id)
            serializer = self.get_serializer(producer, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(created_by=self.request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Producer.DoesNotExist:
            # If no producer exists, proceed with the normal creation flow
            return super().create(request, *args, **kwargs)
        
class ConsumerViewSet(viewsets.ModelViewSet):
    queryset = Consumer.objects.all()
    serializer_class = ConsumerSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def create(self, request, *args, **kwargs):
        applicant_id = request.data.get('applicant')

        if not applicant_id:
            return Response({"error": "Applicant is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if a Producer already exists for this applicant
        try:
            consumer = Consumer.objects.get(applicant_id=applicant_id, created_by=self.request.user.id)
            serializer = self.get_serializer(consumer, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(created_by=self.request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Consumer.DoesNotExist:
            # If no producer exists, proceed with the normal creation flow
            return super().create(request, *args, **kwargs)
        
class CollectorViewSet(viewsets.ModelViewSet):
    queryset = Collector.objects.all()
    serializer_class = CollectorSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def create(self, request, *args, **kwargs):
        applicant_id = request.data.get('applicant')

        if not applicant_id:
            return Response({"error": "Applicant is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if a Producer already exists for this applicant
        try:
            consumer = Collector.objects.get(applicant_id=applicant_id, created_by=self.request.user.id)
            serializer = self.get_serializer(consumer, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(created_by=self.request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Collector.DoesNotExist:
            # If no producer exists, proceed with the normal creation flow
            return super().create(request, *args, **kwargs)

class RecyclerViewSet(viewsets.ModelViewSet):
    queryset = Recycler.objects.all()
    serializer_class = RecyclerSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def create(self, request, *args, **kwargs):
        applicant_id = request.data.get('applicant')

        if not applicant_id:
            return Response({"error": "Applicant is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if a Producer already exists for this applicant
        try:
            recycler = Recycler.objects.get(applicant_id=applicant_id, created_by=self.request.user.id)
            serializer = self.get_serializer(recycler, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(created_by=self.request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Recycler.DoesNotExist:
            # If no producer exists, proceed with the normal creation flow
            return super().create(request, *args, **kwargs)
        
class RawMaterialViewSet(viewsets.ModelViewSet):
    queryset = RawMaterial.objects.all()
    serializer_class = RawMaterialSerializer
    permission_classes = [permissions.IsAuthenticated]

# class DivisionViewSet(viewsets.ReadOnlyModelViewSet):
#     """
#     API endpoint that allows divisions to be viewed.
#     """
#     queryset = TblDivisions.objects.all()
#     serializer_class = DivisionSerializer

class DistrictViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows districts to be viewed.
    """
    queryset = TblDistricts.objects.all()
    serializer_class = DistrictSerializer

class TehsilViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows tehsils to be viewed.
    """
    queryset = TblTehsils.objects.all()
    serializer_class = TehsilSerializer

    def get_queryset(self):
        """
        Optionally restrict the queryset to tehsils of a specific district.
        """
        queryset = super().get_queryset()
        district_id = self.request.query_params.get('district_id')  # Get district_id from query params
        if district_id:
            queryset = queryset.filter(district_id=district_id)  # Filter by district_id
        return queryset

class UserGroupsView(generics.ListAPIView):
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.groups.all()

class UserGroupsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GroupSerializer

    def get_queryset(self):
        return self.request.user.groups.all()
    
class ApplicationAssignmentViewSet(viewsets.ModelViewSet):
    queryset = ApplicationAssignment.objects.all()
    serializer_class = ApplicationAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        return self.request.user.groups.all()
    
    @action(detail=False, methods=['get'])
    def by_applicant(self, request):
        applicant_id = request.query_params.get('applicant_id')
        if applicant_id:
            profiles = self.get_queryset().filter(applicant_id=applicant_id)
            serializer = self.get_serializer(profiles, many=True)
            return Response(serializer.data)
        return Response({'error': 'applicant_id is required'}, status=400)

    def perform_create(self, serializer):
    # Ensure the applicant is correctly passed to the serializer
        print('its in Application Assignment!')
        # print(instance.assigned_group)
        applicant_id = self.request.data.get('applicant')
        if not applicant_id:
            raise ValidationError({"applicant": "Applicant is required."})

        try:
            # Fetch the ApplicantDetail instance
            applicant = ApplicantDetail.objects.get(id=applicant_id)
        except ApplicantDetail.DoesNotExist:
            raise ValidationError({"applicant": "Invalid applicant ID."})

        # Save the ApplicationAssignment instance
        instance = serializer.save(created_by=self.request.user, applicant=applicant)

        # Update the assigned_group in the related ApplicantDetail
        print(instance.assigned_group)
        applicant.assigned_group = instance.assigned_group
        applicant.application_status = 'In Process'
        applicant.save()

def get_original_host(request):
    # Prefer HTTP_ORIGIN as it is more reliable for CORS requests
    origin = request.META.get('HTTP_ORIGIN', '')

    # Fallback to HTTP_REFERER if HTTP_ORIGIN is not available
    if not origin:
        referer = request.META.get('HTTP_REFERER', '')
        if referer:
            # Extract scheme + host from the referer URL
            from urllib.parse import urlparse
            parsed_url = urlparse(referer)
            origin = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return origin

class ApplicantDocumentsViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = ApplicantDocuments.objects.all()
    serializer_class = ApplicanDocumentsSerializer
    def get_serializer_context(self):
        # Get the original host and pass it to the serializer context
        context = super().get_serializer_context()
        context['original_host'] = get_original_host(self.request)
        return context

    def create(self, request, *args, **kwargs):
        document_description = request.data.get("document_description")
        applicant_id = request.data.get("applicant")
        document = request.data.get("document")

        if not applicant_id or not document_description or not document:
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Save the document
            applicant = get_object_or_404(ApplicantDetail, id=applicant_id)
            document_instance = ApplicantDocuments.objects.create(
                applicant=applicant,
                document=document,
                document_description=document_description,
                created_by=request.user,
            )

            # Check if the document description matches the fee verification
            if document_description == "Fee Verification from Treasury/District Accounts Office":
                unsettled_fee = ApplicantFee.objects.filter(applicant=applicant, is_settled=False).first()
                if unsettled_fee:
                    unsettled_fee.is_settled = True
                    unsettled_fee.save()
                    
            # Serialize the saved document instance
            serializer = self.get_serializer(document_instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Modulo(Func):
    """
    Custom function to perform modulo operation in Django ORM.
    """
    function = "MOD"
    template = "%(function)s(%(expressions)s)"
    output_field = IntegerField()

class FetchStatisticsViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for fetching application statistics grouped by assigned_group.
    """

    def list(self, request):
        # Get all groups assigned to the user
        user_groups = request.user.groups.all()
        
        # If the user is not assigned to any group, return an empty response
        if not user_groups.exists():
            return Response({})
        
        # Extract the actual group names of the user
        assigned_group_names = [group.name for group in user_groups]

        # Check if the user is in 'Super' group
        is_super_user = "Super" in assigned_group_names
        
        # If you only want to filter by user groups (except for Super special handling),
        # you can do something like:
        allowed_groups = [group[0] for group in USER_GROUPS]

        # Fetch counts for assigned groups
        statistics = (
            ApplicantDetail.objects
            .filter(assigned_group__in=allowed_groups)
            .values('assigned_group')
            .annotate(count=Count('id'))
        )

        # Create a dictionary that initializes counts for "All-Applications" and "Challan-Downloaded"
        # plus each group the user has
        if is_super_user:
            result = {
                group: 0
                for group in ["All-Applications", "Challan-Downloaded"] + allowed_groups
            }
            # "All-Applications" -> total number of applicants
            result["All-Applications"] = ApplicantDetail.objects.count()
            # "Challan-Downloaded" -> total with application_status != "Created"
            result["Challan-Downloaded"] = ApplicantDetail.objects.filter(
                application_status="Fee Challan"
            ).count()
            
            # If the group is LSO, add LSO1, LSO2, and LSO3 right after
            lso_submitted = ApplicationSubmitted.objects.annotate(
                mod_value=Modulo(F('id'), 3)
            )

            lso1_ids = lso_submitted.filter(mod_value=1).values_list('applicant_id', flat=True)
            lso2_ids = lso_submitted.filter(mod_value=2).values_list('applicant_id', flat=True)
            lso3_ids = lso_submitted.filter(mod_value=0).values_list('applicant_id', flat=True)

            result["LSO1"] = ApplicantDetail.objects.filter(assigned_group = 'LSO', id__in=lso1_ids).count()
            result["LSO2"] = ApplicantDetail.objects.filter(assigned_group = 'LSO', id__in=lso2_ids).count()
            result["LSO3"] = ApplicantDetail.objects.filter(assigned_group = 'LSO', id__in=lso3_ids).count()

        else:
            result = {
                group: 0
                for group in allowed_groups
            }

        # Fill in actual counts for each group
        for stat in statistics:
            result[stat['assigned_group']] = stat['count']



        # Otherwise, return everything
        return Response(result)
    
    # def list(self, request):
    #     user_groups = request.user.groups.all()  # Get all groups assigned to the user
    #     user_group_names = [group[0] for group in USER_GROUPS]  # Extract valid group names


    #     # Extract the names of the user's groups
    #     assigned_group_names = [group.name for group in user_groups]

    #     # Initialize highest_group and track the highest index
    #     highest_group = None
    #     highest_index = -1

    #     # Iterate over user_group_names to find the highest-ranking group
    #     for group in assigned_group_names:
    #         if group in user_group_names:
    #             current_index = user_group_names.index(group)
    #             if current_index > highest_index:  # Only assign if the index is higher
    #                 highest_group = group
    #                 highest_index = current_index

    #     if not highest_group:
    #         return Response({"error": "User group is not valid or assigned"}, status=400)

    #     # Get all groups up to and including the highest-ranking group
    #     #allowed_groups = user_group_names[:highest_index + 1]
    #     allowed_groups = user_group_names

    #     # Fetch statistics for these groups
    #     statistics = (
    #         ApplicantDetail.objects #.filter(application_status='Submitted')
    #         .filter(assigned_group__in=allowed_groups)
    #         .values('assigned_group')
    #         .annotate(count=Count('id'))
    #     )

    #     # Create a dictionary with 0 as default for all allowed groups
    #     result = {group: 0 for group in ["All-Applications", "Challan-Downloaded"] + allowed_groups}

    #     # Update the result with actual counts
    #     for stat in statistics:
    #         result[stat['assigned_group']] = stat['count']

    #     # # Add the count for "All-Applications"
    #     result["All-Applications"] = ApplicantDetail.objects.count()

    #     # # Add the count for "FeeSubmitted"
    #     result["Challan-Downloaded"] = ApplicantDetail.objects.exclude(
    #         application_status="Created"
    #     ).count()
        
    #     return Response(result)


def generate_license_pdf(request):
    # Get parameters from the request
    applicant_id = request.GET.get("applicant_id")
    tracking_number = request.GET.get("tracking_number")

    # Fetch ApplicantDetail based on the given parameter
    if applicant_id:
        applicant = get_object_or_404(ApplicantDetail, id=applicant_id)
    elif tracking_number:
        applicant = get_object_or_404(ApplicantDetail, tracking_number=tracking_number)
    else:
        return JsonResponse({"error": "Either 'applicant_id' or 'tracking_number' must be provided."}, status=400)

    # Fetch BusinessProfile linked to the ApplicantDetail
    business_profile = applicant.businessprofile if hasattr(applicant, 'businessprofile') else None

    # Define data for the PDF
    pdf_data = {
        "license_number": applicant.tracking_number,
        "license_duration": "1 Year",  # You can customize this value
        "owner_name": f"{applicant.first_name} {applicant.last_name or ''}",
        "business_name": business_profile.name if business_profile else "N/A",
        "address": business_profile.postal_address if business_profile else "N/A",
        "cnic_number": applicant.cnic,
    }

    # Create the HTML content for the PDF
    html_content = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
            }}
            .header {{
                text-align: center;
                font-size: 24px;
                margin-bottom: 20px;
            }}
            .content {{
                margin: 0 20px;
                line-height: 1.5;
            }}
            .content div {{
                margin: 10px 0;
            }}
        </style>
    </head>
    <body>
        <div class="header">Plastic License Certificate</div>
        <div class="content">
            <div><strong>License Number:</strong> {pdf_data['license_number']}</div>
            <div><strong>License Duration:</strong> {pdf_data['license_duration']}</div>
            <div><strong>Owner Name:</strong> {pdf_data['owner_name']}</div>
            <div><strong>Business Name:</strong> {pdf_data['business_name']}</div>
            <div><strong>Address:</strong> {pdf_data['address']}</div>
            <div><strong>CNIC Number:</strong> {pdf_data['cnic_number']}</div>
        </div>
    </body>
    </html>
    """

    # Generate the PDF using pdfkit
    try:
        pdf = pdfkit.from_string(html_content, False)  # Generate PDF as binary data
    except Exception as e:
        return JsonResponse({"error": f"PDF generation failed: {str(e)}"}, status=500)

    # Return the PDF as a response
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f"inline; filename=license_{applicant.tracking_number}.pdf"
    return response

# @login_required
def download_latest_document(request):
    # Get the logged-in user
    user = request.user

    # Validate the applicant associated with the logged-in user
    applicant = get_object_or_404(ApplicantDetail, created_by=user.id)

    # Get document description from request parameters
    document_description = request.GET.get("document_description")
    if not document_description:
        return JsonResponse({"error": "Document description parameter is required."}, status=400)

    # Query the latest document matching the applicant and document description
    try:
        document = (
            ApplicantDocuments.objects.filter(
                applicant=applicant,
                document_description=document_description
            )
            .order_by("-created_at")  # Latest document first
            .first()
        )

        if not document:
            return JsonResponse(
                {"error": f"No document found with description '{document_description}'."},
                status=404
            )

        # Prepare the response for file download
        response = HttpResponse(document.document.open(), content_type="application/octet-stream")
        response["Content-Disposition"] = f"attachment; filename={document.document.name.split('/')[-1]}"
        return response

    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

class ApplicantStatisticsView(APIView):
    """
    API to calculate applicant statistics and return details for the grid.
    """

    def get(self, request):
        # Aggregated counts for all applicants
        applications_count = ApplicantDetail.objects.exclude(application_status='Created').count()
        licenses_count = ApplicantDetail.objects.filter(application_status='Completed').count()
        in_progress_count = ApplicantDetail.objects.filter(
            ~Q(application_status='Created') & 
            ~Q(application_status='Completed') & 
            ~Q(application_status='Rejected')
        ).count()

        # District-wise statistics grouped by 'registration_for'
        district_statistics = ApplicantDetail.objects.exclude(application_status='Created') \
            .values('registration_for', 'businessprofile__district__district_name') \
            .annotate(count=Count('id'))

        
        # Statistics filtered by 'registration_for'
        registration_statistics = ApplicantDetail.objects \
            .exclude(registration_for__isnull=True) \
            .values('registration_for') \
            .annotate(
                Applications=Count('id', filter=~Q(application_status='Created')),
                Licenses=Count('id', filter=Q(application_status='Completed')),
                InProgress=Count('id', filter=~Q(application_status='Created') &
                                                ~Q(application_status='Completed') &
                                                ~Q(application_status='Rejected')),
            )


        # Grid data
        grid_data = ApplicantDetail.objects.values(
            'first_name',
            'last_name',
            'cnic',
            'mobile_no',
            'application_status',
            'tracking_number',
            'assigned_group',
            'registration_for',
            'businessprofile__district__district_name'  # Include district name
        )

        response_data = {
            'statistics': {
                'Applications': applications_count,
                'Licenses': licenses_count,
                'InProgress': in_progress_count
            },
            'district_data': list(district_statistics),
            'grid_data': list(grid_data),
            'registration_statistics': list(registration_statistics),  # New key
        }

        return Response(response_data)

def download_file(request, file_name):
    # Construct the full file path
    file_path = os.path.join("media/documents", file_name)
    if os.path.exists(file_path):
        # # Serve the file as a response
        # response = FileResponse(open(file_path, "rb"), as_attachment=True)
        # return response
        # Serve the file as a response
        response = FileResponse(open(file_path, "rb"), as_attachment=False)
        # Set Content-Disposition to inline for viewing
        response["Content-Disposition"] = f'inline; filename="{file_name}"'
        return response
    else:
        raise Http404("File does not exist")

class ApplicantAlertsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        
        # 1) Filter ApplicantDetail by user
        #    (Adjust the filter if your ownership logic is different.)
        applicants = ApplicantDetail.objects.filter(created_by=user,
            assigned_group='APPLICANT'
        )

        # 2) Get IDs of those applicants
        applicant_ids = applicants.values_list('id', flat=True)

        # 3) Query ApplicationAssignment for those IDs + assigned_group='APPLICANT'
        assignments = ApplicationAssignment.objects.filter(
            applicant_id__in=applicant_ids,
            assigned_group='APPLICANT',
            remarks__isnull=False
        ).exclude(
            Q(remarks__isnull=True) | Q(remarks__iexact='undefined')
        ).order_by('-created_at')  # optional ordering by most recent

        # 4) Serialize them for return
        serializer = ApplicantAlertsSerializer(assignments, many=True)
        return Response(serializer.data, status=200)