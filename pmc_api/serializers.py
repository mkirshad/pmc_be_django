
from rest_framework import serializers
from .models import *
from django.db.models import Sum, FloatField
from django.db.models.functions import Cast
from django.utils.timezone import localtime


class PlasticItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlasticItems
        fields = '__all__'


class ProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = '__all__'


class ByProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ByProducts
        fields = '__all__'


class ProducerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producer
        fields = '__all__'


class ConsumerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consumer
        fields = '__all__'
        
class CollectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collector
        fields = '__all__'
        
class RecyclerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recycler
        fields = '__all__'
        
class ApplicanDocumentsSerializer(serializers.ModelSerializer):
    applicant = serializers.PrimaryKeyRelatedField(queryset=ApplicantDetail.objects.all())

    class Meta:
        model = ApplicantDocuments
        fields = '__all__'
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Retrieve the request from the context
        request = self.context.get("request")
        if request and representation.get("document"):
            # Generate an absolute URL for the document
            document_path = representation["document"]
            document_path = document_path.replace('/media/documents/', '/api/pmc/media/documents/')
            
            if '.com' in document_path or '.pk' in document_path:
                # Replace http with https if the URL contains .com
                document_path = document_path.replace('http://', 'https://')
            elif 'localhost' in document_path or '127.0.0.1' in document_path:
                # For localhost or IP-based URLs, leave them as they are
                document_path = document_path
            else:
                # Handle other cases as needed, e.g., non-standard domains
                pass
            
            representation["document"] = document_path

        return representation

class ApplicationSubmittedSerializer(serializers.ModelSerializer):

    class Meta:
        model = ApplicationSubmitted
        fields = '__all__'
        
class RawMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawMaterial
        fields = '__all__'

# class DivisionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TblDivisions
#         fields = ['id', 'division_name']

class DistrictSerializer(serializers.ModelSerializer):

    class Meta:
        model = TblDistricts
        fields = ['district_id', 'district_name', 'district_code']

class DistrictGEOMSerializer(serializers.ModelSerializer):

    class Meta:
        model = TblDistricts
        geo_field = "geom"  # Field that contains geometry
        fields = ['district_id', 'district_name', 'district_code', 'geom']
        
class TehsilSerializer(serializers.ModelSerializer):
    district = DistrictSerializer()

    class Meta:
        model = TblTehsils
        fields = ['tehsil_id', 'tehsil_name', 'tehsil_code', 'district']


class BusinessProfileSerializer(serializers.ModelSerializer):
    #applicant = ApplicantDetailSerializer(read_only=True)  # Include the nested applicant data
    district_name = serializers.ReadOnlyField(source="district.district_name")  # Extract district name
    tehsil_name = serializers.ReadOnlyField(source="tehsil.tehsil_name")  # Extract tehsil name
    class Meta:
        model = BusinessProfile
        fields = '__all__'  # Includes all fields in the model
        read_only_fields = ['updated_by', 'updated_at']  # Make these fields read-only

    # def validate_ntn_strn_pra_no_company(self, value):
    #     if self.instance and self.instance.entity_type == 'individual':
    #         return value
    #     if not value:
    #         raise serializers.ValidationError("NTN/STRN/PRA No. is required for companies.")
    #     return value
    #
    # def validate(self, data):
    #     entity_type = data.get('entity_type')
    #     ntn_strn_pra_no_company = data.get('ntn_strn_pra_no_company')
    #     return data

class ApplicationAssignmentSerializer(serializers.ModelSerializer):
    applicant = serializers.PrimaryKeyRelatedField(queryset=ApplicantDetail.objects.all())
    created_by = serializers.StringRelatedField(read_only=True)
    created_by_group = serializers.SerializerMethodField()    

    def get_created_by_group(self, obj):
        user = obj.created_by
        user_groups = user.groups.values_list('name', flat=True)

        # Check if username matches any group name
        matching_group = next((g for g in user_groups if g.lower() == user.username.lower()), None)

        # If match found, return it; otherwise return first group (if exists)
        return matching_group if matching_group else (user_groups[0] if user_groups else None)
    
    class Meta:
        model = ApplicationAssignment
        fields = '__all__'  # Include all fields of the model
        read_only_fields = ['created_by', 'created_at', 'updated_at']

class ApplicantFieldResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicantFieldResponse
        fields = '__all__'  # Include all fields of the model

class ApplicantFeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicantFee
        fields = '__all__'  # Include all fields of the model

class ApplicantManualFieldsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicantManualFields
        fields = '__all__'

class PSIDTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PSIDTracking
        fields = ['consumer_number', 'payment_status', 'amount_paid', 'paid_date', 'paid_time', 'bank_code']

class ApplicantDetailSerializer(serializers.ModelSerializer):
    businessprofile = BusinessProfileSerializer(read_only=True)
    producer = ProducerSerializer(read_only=True)
    consumer = ConsumerSerializer(read_only=True)
    collector = CollectorSerializer(read_only=True)
    recycler = RecyclerSerializer(read_only=True)
    applicationassignment = serializers.SerializerMethodField()
    applicationdocument = ApplicanDocumentsSerializer(many=True, read_only=True)
    submittedapplication = ApplicationSubmittedSerializer(read_only=True)
    field_responses = ApplicantFieldResponseSerializer(many=True, read_only=True)
    applicantfees = ApplicantFeeSerializer(many=True, read_only=True)
    manual_fields = ApplicantManualFieldsSerializer(read_only=True)
    has_identity_document = serializers.SerializerMethodField()
    has_fee_challan = serializers.SerializerMethodField()
    is_downloaded_fee_challan = serializers.SerializerMethodField()
    psid_tracking = serializers.SerializerMethodField()  # Use a method field to filter PSIDTracking
    
    #consumer = ConsumerSerializer(read_only=True)
    #collector = CollectorSerializer(read_only=True)
    #recycler = RecyclerSerializer(read_only=True)
    class Meta:
        model = ApplicantDetail
        fields = '__all__'  # Include all fields of the model
        read_only_fields = ['created_by', 'created_at', 'updated_at']
        # exclude = ['tracking_hash']

    def get_has_identity_document(self, obj):
        """
        Check if an 'Identity Document' exists for this applicant.
        """
        return ApplicantDocuments.objects.filter(applicant=obj, document_description='Identity Document').exists()

    def get_has_fee_challan(self, obj):
        """
        Check if a 'Fee Challan' exists for this applicant.
        """
        return ApplicantDocuments.objects.filter(applicant=obj, document_description='Fee Challan').exists() or PSIDTracking.objects.filter(applicant=obj, payment_status='PAID').exists()
    
    def get_is_downloaded_fee_challan(self, obj):
        return ApplicantFee.objects.filter(applicant=obj).exists() and not PSIDTracking.objects.filter(applicant=obj).exists()

    def get_psid_tracking(self, obj):
        """
        Return only those PSIDs with payment_status = 'PAID'.
        """
        paid_psids = PSIDTracking.objects.filter(applicant=obj, payment_status='PAID')
        return PSIDTrackingSerializer(paid_psids, many=True).data

    def get_applicationassignment(self, obj):
        assignments = obj.applicationassignment.all().order_by('created_at')
        return ApplicationAssignmentSerializer(assignments, many=True).data
class LicenseSerializer(serializers.ModelSerializer):
    district_name = serializers.SerializerMethodField()
    tehsil_name = serializers.SerializerMethodField()
    city_name = serializers.SerializerMethodField()
    is_active_display = serializers.SerializerMethodField()  # New SerializerMethodField for is_active
    class Meta:
        model = License
        fields = '__all__'  # Include all fields of the model
        read_only_fields = ['created_by', 'created_at', 'updated_at']
    def get_district_name(self, obj):
        """
        Return the district name from the applicant's BusinessProfile,
        or None if not found.
        """
        applicant = ApplicantDetail.objects.filter(id=obj.applicant_id).first()
        if applicant and hasattr(applicant, 'businessprofile') and applicant.businessprofile:
            district = applicant.businessprofile.district
            if district:  # district is a TblDistricts instance
                return district.district_name
        return None

    def get_tehsil_name(self, obj):
        """
        Return the tehsil name from the applicant's BusinessProfile,
        or None if not found.
        """
        applicant = ApplicantDetail.objects.filter(id=obj.applicant_id).first()
        if applicant and hasattr(applicant, 'businessprofile') and applicant.businessprofile:
            tehsil = applicant.businessprofile.tehsil
            if tehsil:  # tehsil is a TblTehsils instance
                return tehsil.tehsil_name
        return None

    def get_city_name(self, obj):
        """
        Return the city_town_village field from the applicant's BusinessProfile,
        or None if not found.
        """
        applicant = ApplicantDetail.objects.filter(id=obj.applicant_id).first()
        if applicant and hasattr(applicant, 'businessprofile') and applicant.businessprofile:
            return applicant.businessprofile.city_town_village
        return None

    def get_is_active_display(self, obj):
        """
        Return 'Yes' if is_active is True, otherwise 'No'.
        """
        return "Yes" if obj.is_active else "No"

    # Optional: If you want to exclude the original is_active field and only use is_active_display,
    # you can override the to_representation method.
    def to_representation(self, instance):
        """
        Override to_representation to replace 'is_active' with 'is_active_display'.
        """
        representation = super().to_representation(instance)
        representation['is_active'] = self.get_is_active_display(instance)
        # Optionally, remove 'is_active_display' if not needed
        representation.pop('is_active_display', None)
        return representation

class ApplicantDetailMainListSerializer(serializers.ModelSerializer):
    applicationassignment = ApplicationAssignmentSerializer(many=True, read_only=True)
    applicantfees = ApplicantFeeSerializer(many=True, read_only=True)
    submittedapplication = ApplicationSubmittedSerializer(read_only=True)
    created_by_username = serializers.SerializerMethodField()

    class Meta:
        model = ApplicantDetail
        fields = '__all__'  # Include all fields of the model
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def get_created_by_username(self, obj):
        # Safely access the username of the user who created the object
        return obj.created_by.username if obj.created_by else None

class ApplicantAlertsSerializer(serializers.ModelSerializer):
    # We can fetch the tracking_number from the related applicant
    tracking_number = serializers.CharField(source='applicant.tracking_number', read_only=True)
    # Optionally fetch the applicant’s ID
    applicant_id = serializers.IntegerField(source='applicant.id', read_only=True)
    # Maybe also created_at for the remark
    created_at = serializers.SerializerMethodField()
    url_sub_part = serializers.SerializerMethodField()  # ✅ New field for URL sub-part

    def get_created_at(self, obj):
        # Convert obj.created_at to string, then slice
        datetime_str = obj.created_at.isoformat()
        return datetime_str[:19]

    def get_url_sub_part(self, obj):
        """Generate URL sub-part dynamically"""
        if obj.assigned_group == "Download License":
            return "/home-license"
        return f"spuid-signup/{obj.applicant.id}/"  # ✅ Normal case

    class Meta:
        model = ApplicationAssignment
        fields = ['id', 'applicant_id', 'tracking_number', 'remarks', 'created_at', 'url_sub_part']
        

class ApplicantLocationSerializer(serializers.ModelSerializer):
    # District from BusinessProfile
    district_name = serializers.CharField(
        source='businessprofile.district.district_name',
        read_only=True
    )
    
    district_id = serializers.CharField(
        source='businessprofile.district_id',
        read_only=True
    )
        
    # Tehsil from BusinessProfile
    tehsil_name = serializers.CharField(
        source='businessprofile.tehsil.tehsil_name',
        read_only=True
    )
    # City from BusinessProfile
    # city_town_village = serializers.CharField(
    #     source='businessprofile.city_town_village',
    #     read_only=True
    # )
    # # Business Name from BusinessProfile
    # business_name = serializers.CharField(
    #     source='businessprofile.name',
    #     read_only=True
    # )
    # Business Name from BusinessProfile (Converted to SerializerMethodField for conditional logic)
    business_name = serializers.SerializerMethodField()
    # Postal Address from BusinessProfile
    postal_address = serializers.CharField(
        source='businessprofile.postal_address',
        read_only=True
    )

    # If you no longer want lat/lng from BusinessProfile, remove those
    # and instead use manual_fields. For example:
    latitude = serializers.DecimalField(
        source='manual_fields.latitude',
        max_digits=9,
        decimal_places=6,
        read_only=True
    )
    longitude = serializers.DecimalField(
        source='manual_fields.longitude',
        max_digits=9,
        decimal_places=6,
        read_only=True
    )
    
    category = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    # New Field: Material Flow in Kg per Day
    material_flow_kg_per_day = serializers.SerializerMethodField()

    class Meta:
        model = ApplicantDetail
        fields = [
            'id',
            'category',
            'full_name',
            # 'applicant_designation',
            'district_name',
            'district_id',
            'tehsil_name',
            # 'city_town_village',
            'business_name',
            'postal_address',
            'latitude',
            'longitude',
            'material_flow_kg_per_day',
        ]

    def get_category(self, obj):
        """
        Return 'Distributor' if the model field is 'Consumer',
        otherwise return the actual value.
        """
        if obj.registration_for == 'Consumer':
            return 'Distributor'
        return obj.registration_for

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name or ''}".strip()

    def get_material_flow_kg_per_day(self, obj):
        """
        Retrieves the material flow in Kg per day based on the applicant's category.
        """
        category = self.get_category(obj)
        
        if category == 'Producer':
            try:
                producer = obj.producer  # Access related Producer model
                return producer.total_capacity_value if producer.total_capacity_value is not None else 0
            except Producer.DoesNotExist:
                return 0

        elif category == 'Distributor' or category == 'Consumer':
            # Assuming 'Distributor' is treated similarly to 'Consumer'
            try:
                consumer = obj.consumer  # Access related Consumer model
                return consumer.consumption if consumer.consumption is not None else 0
            except Consumer.DoesNotExist:
                return 0

        elif category == 'Collector':
            try:
                collector = obj.collector  # Access related Collector model
                return collector.total_capacity_value if collector.total_capacity_value is not None else 0
            except Collector.DoesNotExist:
                return 0

        elif category == 'Recycler':
            try:
                recycler = obj.recycler  # Access related Recycler model
                return recycler.total_capacity_value if hasattr(recycler, 'total_capacity_value') and recycler.total_capacity_value is not None else 0
            except Recycler.DoesNotExist:
                return 0

        else:
            # Default case if category is unrecognized
            return 0
        
    def get_business_name(self, obj):
        """
        If business_name is 'Trader', return the applicant's full name.
        Otherwise, return the actual business_name from BusinessProfile.
        """
        business_name = getattr(obj.businessprofile, 'name', None)
        if business_name == 'Trader':
            return self.get_full_name(obj)
        return business_name
    
class DistrictPlasticStatsSerializer(serializers.ModelSerializer):
    produced_kg_per_day = serializers.SerializerMethodField()
    distributed_kg_per_day = serializers.SerializerMethodField()
    collected_kg_per_day = serializers.SerializerMethodField()
    waste_disposed_kg_per_day = serializers.SerializerMethodField()
    waste_collected_kg_per_day = serializers.SerializerMethodField()
    unmanaged_waste_kg_per_day = serializers.SerializerMethodField()
    recycling_efficiency = serializers.SerializerMethodField()

    class Meta:
        model = TblDistricts
        fields = [
            "district_id",
            "district_name",
            "produced_kg_per_day",
            "distributed_kg_per_day",
            "collected_kg_per_day",
            "waste_disposed_kg_per_day",
            "waste_collected_kg_per_day",
            "unmanaged_waste_kg_per_day",
            "recycling_efficiency",
        ]

    def get_model_queryset(self, district, model, field_to_sum):
        """
        Fetches data from the appropriate model based on `registration_for`.
        Ensures only relevant applicants with the correct `registration_for` are considered.
        Filters out applicants that are 'In Process' and not assigned to groups 'APPLICANT', 'LSO', 'LSM', or 'DO'.
        """
        excluded_groups = ["APPLICANT", "LSO", "LSM", "DO"]

        return (
            model.objects.filter(
                applicant__businessprofile__district=district,
                applicant__registration_for=model.__name__,  # Ensure matching model
                applicant__application_status="In Process",  # Only 'In Process' applicants
            )
            .exclude(applicant__assigned_group__in=excluded_groups)  # Exclude listed groups
            .aggregate(total=Sum(field_to_sum, default=0))["total"]
            or 0
        )
        
    def get_produced_kg_per_day(self, obj):
        """Sum of production capacity for all producers in the district"""
        return self.get_model_queryset(obj, Producer, "total_capacity_value")

    def get_distributed_kg_per_day(self, obj):
        """Sum of consumption for all consumers in the district"""
        return (
            Consumer.objects.filter(applicant__businessprofile__district=obj)
            .exclude(consumption="")  # Exclude empty strings
            .annotate(consumption_float=Cast("consumption", FloatField()))  # Convert to Float
            .aggregate(total=Sum("consumption_float", default=0))["total"]
            or 0
        )

    def get_collected_kg_per_day(self, obj):
        """Sum of collection capacity for all collectors in the district"""
        return self.get_model_queryset(obj, Collector, "total_capacity_value")

    def get_waste_collected_kg_per_day(self, obj):
        """Sum of waste collected by recyclers"""
        return sum(
            recycler.get_total_waste_collected()
            for recycler in Recycler.objects.filter(applicant__businessprofile__district=obj)
        )

    def get_waste_disposed_kg_per_day(self, obj):
        """Sum of waste disposed from recyclers' JSONField data"""
        return sum(
            recycler.get_total_waste_disposed()
            for recycler in Recycler.objects.filter(applicant__businessprofile__district=obj)
        )

    def get_recycling_efficiency(self, obj):
        """Calculate recycling efficiency as (Recycled Waste / Collected Waste) * 100"""
        collected_by_collectors = self.get_collected_kg_per_day(obj)  # From Collector model
        collected_by_recyclers = self.get_waste_collected_kg_per_day(obj)  # From Recycler model
        max_collected = max(collected_by_collectors, collected_by_recyclers)
        disposed_by_recyclers = self.get_waste_disposed_kg_per_day(obj)  # From Recycler model

        if max_collected == 0:
            return 0  # Avoid division by zero

        return max(0, round((disposed_by_recyclers / max_collected) * 100, 2))  # Avoid negative efficiency

    def get_unmanaged_waste_kg_per_day(self, obj):
        """
        Calculate Unmanaged Waste = max(Waste Collected by Collectors, Waste Disposed) - Waste Disposed.
        Ensures unmanaged waste is never negative.
        """
        collected_by_collectors = self.get_collected_kg_per_day(obj)  # From Collector model
        collected_by_recyclers = self.get_waste_collected_kg_per_day(obj)  # From Recycler model
        disposed_by_recyclers = self.get_waste_disposed_kg_per_day(obj)  # From Recycler model

        # Take the maximum value and subtract disposed waste
        unmanaged_waste = max(collected_by_collectors, collected_by_recyclers) - disposed_by_recyclers

        return max(0, unmanaged_waste)  # Ensure it does not go negative

class InspectionReportSerializer(serializers.ModelSerializer):
    district = serializers.CharField(source="district.district_name", read_only=True)  # ✅ Return district name instead of ID
    class Meta:
        model = InspectionReport
        fields = '__all__'

# Define Summary Serializer
class DistrictSummarySerializer(serializers.Serializer):
    district = serializers.CharField(source="district__district_name")
    total_inspections = serializers.IntegerField()
    total_notices_issued = serializers.IntegerField()
    total_plastic_bags_confiscated = serializers.FloatField()
    total_confiscated_plastic = serializers.FloatField()
    total_firs_registered = serializers.IntegerField()
    total_premises_sealed = serializers.IntegerField()
    total_complaints_filed = serializers.IntegerField()

    # ✅ Added KPIs
    total_fine_amount = serializers.FloatField()
    total_fine_recovered = serializers.FloatField()
    pending_fine_amount = serializers.FloatField()

    total_fines_pending = serializers.IntegerField()
    total_fines_partial = serializers.IntegerField()
    total_fines_recovered = serializers.IntegerField()

    total_de_sealed_premises = serializers.IntegerField()

class DistrictPlasticCommitteeDocumentSerializer(serializers.ModelSerializer):
    district_name = serializers.CharField(source="district.district_name", read_only=True)
    uploaded_at = serializers.SerializerMethodField()
    uploaded_by_name = serializers.SerializerMethodField()  # First Name + Last Name

    class Meta:
        model = DistrictPlasticCommitteeDocument
        fields = ["id", "district_id", "district_name", "document_type", "document", "document_date", "uploaded_at", "uploaded_by_name", "title"]

    def get_uploaded_at(self, obj):
        return localtime(obj.uploaded_at).strftime("%Y-%m-%d %H:%M:%S")  # Removes time zone

    def get_uploaded_by_name(self, obj):
        if obj.uploaded_by:
            first_name = obj.uploaded_by.first_name or ""
            last_name = obj.uploaded_by.last_name or ""
            full_name = f"{first_name} {last_name}".strip()
            return full_name if full_name else obj.uploaded_by.username
        return "Unknown"

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Retrieve the request from the context
        request = self.context.get("request")
        if request and representation.get("document"):
            # Generate an absolute URL for the document
            document_path = representation["document"]
            document_path = document_path.replace('/media/plastic_committee/', '/api/pmc/media/plastic_committee/')
            
            if '.com' in document_path or '.pk' in document_path:
                # Replace http with https if the URL contains .com
                document_path = document_path.replace('http://', 'https://')
            elif 'localhost' in document_path or '127.0.0.1' in document_path:
                # For localhost or IP-based URLs, leave them as they are
                document_path = document_path
            else:
                # Handle other cases as needed, e.g., non-standard domains
                pass
            
            representation["document"] = document_path

        return representation

class CompetitionRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitionRegistration
        fields = '__all__'