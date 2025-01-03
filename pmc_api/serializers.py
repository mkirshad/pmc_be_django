
from rest_framework import serializers
from .models import *








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
        fields = '__all__'

class ApplicantDetailSerializer(serializers.ModelSerializer):
    businessprofile = BusinessProfileSerializer(read_only=True)
    producer = ProducerSerializer(read_only=True)
    consumer = ConsumerSerializer(read_only=True)
    collector = CollectorSerializer(read_only=True)
    recycler = RecyclerSerializer(read_only=True)
    applicationassignment = ApplicationAssignmentSerializer(many=True, read_only=True)
    applicationdocument = ApplicanDocumentsSerializer(many=True, read_only=True)
    submittedapplication = ApplicationSubmittedSerializer(read_only=True)
    field_responses = ApplicantFieldResponseSerializer(many=True, read_only=True)
    applicantfees = ApplicantFeeSerializer(many=True, read_only=True)
    manual_fields = ApplicantManualFieldsSerializer(read_only=True)
    has_identity_document = serializers.SerializerMethodField()
    has_fee_challan = serializers.SerializerMethodField()

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

    def get_created_at(self, obj):
        # Convert obj.created_at to string, then slice
        datetime_str = obj.created_at.isoformat()
        return datetime_str[:19]

    class Meta:
        model = ApplicationAssignment
        fields = ['id', 'applicant_id', 'tracking_number', 'remarks', 'created_at']