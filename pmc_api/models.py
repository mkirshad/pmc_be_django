from django.contrib.auth.models import User, Group
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from django.db.models import JSONField

from pmc_api.models_choices import *
from pmc_api.utils import validate_latitude, validate_longitude
from rest_framework import serializers
import uuid
import os
from datetime import datetime, timedelta
from django.utils import timezone

class TblDivisions(models.Model):
    #  gid = models.AutoField()
    division_id = models.AutoField(primary_key=True)
    division_name = models.CharField(max_length=254)
    division_code = models.CharField(max_length=254)

    # geom = models.GeometryField(srid=0, blank=True, null=True)

    def __str__(self):
        return self.division_name

    class Meta:
        managed = False
        db_table = 'tbl_divisions'


class TblDistricts(models.Model):
    # gid = models.AutoField()
    district_id = models.IntegerField(primary_key=True)
    division = models.ForeignKey('TblDivisions', models.DO_NOTHING)
    district_name = models.CharField(max_length=254)
    district_code = models.CharField(max_length=254)
    short_name = models.CharField(max_length=3)
    pitb_district_id = models.IntegerField(null=True, blank=True)
    
    # geom = models.GeometryField(srid=0, blank=True, null=True)

    def __str__(self):
        return self.district_name

    class Meta:
        managed = False
        db_table = 'tbl_districts'
        ordering = ['district_name', ]
        verbose_name_plural = "Districts"
        indexes = [
            models.Index(fields=['district_code'], name='idx_district_code'),
            models.Index(fields=['short_name'], name='idx_district_short_name'),
        ]



class TblTehsils(models.Model):
    # gid = models.AutoField()
    tehsil_id = models.AutoField(primary_key=True)
    district = models.ForeignKey(TblDistricts, models.DO_NOTHING)
    division = models.ForeignKey(TblDivisions, models.DO_NOTHING)
    tehsil_name = models.CharField(max_length=254)
    tehsil_code = models.CharField(unique=True, max_length=254)

    # geom = models.GeometryField(srid=0, blank=True, null=True)
    # extent = models.CharField(max_length=254, blank=True, null=True)
    def __str__(self):
        return self.tehsil_name

    class Meta:
        managed = False
        db_table = 'tbl_tehsils'
        ordering = ['tehsil_name', ]
        indexes = [
            models.Index(fields=['district'], name='idx_tehsil_district'),
            models.Index(fields=['tehsil_code'], name='idx_tehsil_code'),
        ]



def default_value_uuid():
    return uuid.uuid4()


class ApplicantDetail(models.Model):
    registration_for = models.CharField(max_length=10, choices=REG_TYPE_CHOICES, null=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    applicant_designation = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=100, choices=GENDER_CHOICES)
    cnic = models.CharField(max_length=15, help_text='XXXXX-XXXXXXX-X', validators=[
        MinLengthValidator(15),
        RegexValidator(
            regex=r'^\d{5}-\d{7}-\d{1}$',
            message="CNIC must be in the format XXXXX-XXXXXXX-X."
        )
    ], )
    email = models.EmailField(max_length=255, blank=True, null=True)
    mobile_operator = models.CharField(max_length=15, choices=MOBILE_NETWORK_CHOICES, blank=True, null=True)
    mobile_no = models.CharField(max_length=10, help_text='3001234567', validators=[
        MinLengthValidator(10),  # Ensures minimum length is 10
        RegexValidator(
            regex=r'^\d{10}$',
            message="Mobile number must be exactly 10 digits, e.g., '3001234567'."
        )
    ], )
    application_status = models.CharField(max_length=20, choices=APPLICATION_STATUS_CHOICES, default='Created')
    tracking_number = models.CharField(max_length=100, null=True)
    remarks = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_group = models.CharField(max_length=100, null=True, choices=USER_GROUPS)
    tracking_hash = models.CharField(
        max_length=36,  # Standard length for a UUID string
        default=default_value_uuid,
        editable=False,
        unique=False
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        # Check if the application_status is 'Submitted'
        if self.application_status == 'Submitted':
            # Set the assigned_group to 'LSO'
            self.assigned_group = 'LSO'
            
            # Create a record in the ApplicationSubmitted model
            if not ApplicationSubmitted.objects.filter(applicant=self).exists():
                ApplicationSubmitted.objects.create(applicant=self)
        # Check if a BusinessProfile exists for this applicant
        if hasattr(self, 'businessprofile') and self.businessprofile:
            business_profile = self.businessprofile
            district = business_profile.district

            # Ensure district and registration_for exist
            if district and self.registration_for:
                district_code = district.short_name or district.district_name[
                                                       :3].upper() or "XXX"  # Use "XXX" if short_name is missing
                registration_code = self.registration_for[:3].upper()  # First 3 letters of registration_for
                applicant_id = str(self.id).zfill(3)  # Zero-padded applicant ID

                # Generate tracking_number
                self.tracking_number = f"{district_code}-{registration_code}-{applicant_id}"

        # Call the parent save method to save the instance
        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=['application_status'], name='idx_app_status'),
            models.Index(fields=['assigned_group'], name='idx_assigned_group'),
            models.Index(fields=['created_by'], name='idx_created_by'),
            models.Index(fields=['tracking_number'], name='idx_tracking_number'),
            models.Index(fields=['application_status', 'assigned_group'], name='idx_status_group'),
        ]

class ApplicationSubmitted(models.Model):
    applicant = models.OneToOneField(ApplicantDetail, on_delete=models.CASCADE, blank=True, null=True,
                                     related_name='submittedapplication')
    created_at = models.DateTimeField(auto_now_add=True)
    
class BusinessProfile(models.Model):
    entity_type = models.CharField(
        max_length=20, choices=ENTITY_TYPE_CHOICES, default='Individual'
    )
    applicant = models.OneToOneField(ApplicantDetail, on_delete=models.CASCADE, blank=True, null=True,
                                     related_name='businessprofile')
    tracking_number = models.CharField(max_length=100, unique=True, blank=True, null=True)
    # If Individual
    name = models.CharField(max_length=255, blank=True, null=True)
    ntn_strn_pra_no_individual = models.CharField(max_length=20, blank=True, null=True)
    # If Company/Corporation/Partnership
    business_name = models.CharField(max_length=255, blank=True, null=True)
    business_registration_type = models.CharField(
        max_length=50, choices=BUSINESS_REGISTRATION_CHOICES, blank=True, null=True
    )
    business_registration_no = models.CharField(max_length=50, blank=True, null=True)
    ntn_strn_pra_no_company = models.CharField(max_length=20, blank=True, null=True)  # Masking can be applied in forms
    working_days = models.IntegerField(choices=((5, 5), (6, 6), (7, 7)), default=5,
                                       help_text='working days in the week', blank=True, null=True)
    commencement_date = models.DateField(help_text='Date since commencement of Business', blank=True, null=True)
    no_of_workers = models.IntegerField(help_text='Number of workers (including contract labour)', blank=True,
                                        null=True)
    #  Address Detail
    district = models.ForeignKey(TblDistricts, on_delete=models.CASCADE, db_column='district_id',
                                 verbose_name="District", blank=True, null=True)
    tehsil = models.ForeignKey(TblTehsils, on_delete=models.CASCADE, db_column='tehsil_id',
                               verbose_name="Tehsil", blank=True, null=True)
    city_town_village = models.CharField(max_length=256, help_text="Name of City/Town or Village", blank=True,
                                         null=True)
    postal_address = models.TextField(blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    location_latitude = models.DecimalField(max_digits=9, decimal_places=6, validators=[validate_latitude],
                                            help_text='Format: XX.XXXXXX, Range: 20.000000 to 40.000000, Unit: Decimal Degree',
                                            blank=True, null=True)
    location_longitude = models.DecimalField(max_digits=9, decimal_places=6, validators=[validate_longitude],
                                             help_text='Format: XX.XXXXXX, Range: 60.000000 to 80.000000,Unit: Decimal Degree',
                                             blank=True, null=True)
    # Contact Detail
    email = models.EmailField(max_length=255, blank=True, null=True)
    mobile_operator = models.CharField(max_length=15, choices=MOBILE_NETWORK_CHOICES, blank=True, null=True)
    mobile_no = models.CharField(max_length=10, help_text='3001234567', validators=[
        MinLengthValidator(10),  # Ensures minimum length is 10
        RegexValidator(
            regex=r'^\d{10}$',
            message="Mobile number must be exactly 10 digits, e.g., '3001234567'."
        )
    ], blank=True, null=True)
    phone_no = models.CharField(max_length=12, help_text='042-12345678', blank=True, null=True)
    website_address = models.URLField(blank=True, null=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='businessprofilecreatedby')

    def __str__(self):
        return self.business_name or self.name

    class Meta:
        indexes = [
            models.Index(fields=['district'], name='idx_district'),
            models.Index(fields=['tehsil'], name='idx_tehsil'),
            models.Index(fields=['tracking_number'], name='idx_bp_tracking_number'),
        ]


class PlasticItems(models.Model):
    item_name = models.CharField(max_length=255, unique=True)  # single use plastic item name


class Products(models.Model):
    product_name = models.CharField(max_length=255, unique=True)


class ByProducts(models.Model):
    product_name = models.CharField(max_length=255, unique=True)


class Producer(models.Model):
    applicant = models.OneToOneField(ApplicantDetail, on_delete=models.CASCADE)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)

    # Registration details
    registration_required_for = models.JSONField(blank=True, null=True)  # Stores ManufacturingType[]
    registration_required_for_other = models.JSONField(blank=True, null=True)  # Stores ManufacturingType[]
    plain_plastic_sheets_for_food_wrapping = models.JSONField(blank=True, null=True)  # Stores SingleUseSheet[]
    packaging_items = models.JSONField(blank=True, null=True)  # Stores PackagingItems[]

    # Machine and capacity details
    number_of_machines = models.CharField(max_length=255, blank=True, null=True)  # Stores string
    total_capacity_value = models.FloatField(blank=True, null=True)

    # Date of setting up
    date_of_setting_up = models.DateField(blank=True, null=True)

    # Waste management
    total_waste_generated_value = models.FloatField(blank=True, null=True)
    has_waste_storage_capacity = models.CharField(max_length=255, blank=True, null=True,
                                                  choices=[('Available', 'Available'),
                                                           ('Not Available', 'Not Available')])
    waste_disposal_provision = models.CharField(max_length=255, blank=True, null=True,
                                                choices=[('Available', 'Available'),
                                                         ('Not Available', 'Not Available')])
    registration_required_for_other_other_text = models.CharField(max_length=1024, blank=True, null=True)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    # raw material detail
    # Documents
    # flow_diagram = models.FileField(upload_to='diagrams/', blank=True, null=True)
    # consent_permit = models.FileField(upload_to='permit/', blank=True, null=True)


class RawMaterial(models.Model):
    producer = models.ForeignKey(Producer, on_delete=models.CASCADE)
    material_name = models.CharField(max_length=255, unique=True)
    material_description = models.CharField(max_length=255, blank=True, null=True)
    material_quantity_value = models.FloatField(blank=True, null=True)
    material_quantity_unit = models.FloatField(blank=True, null=True)
    material_utilized_quantity_value = models.FloatField(blank=True, null=True)
    material_utilized_quantity_unit = models.FloatField(blank=True, null=True)
    material_import_bought = models.CharField(max_length=255, blank=True, null=True, choices=IMPORT_BOUGHT)
    name_seller_importer = models.CharField(max_length=255, blank=True, null=True)
    is_importer_form_filled = models.BooleanField(default=False)


class Consumer(models.Model):
    applicant = models.OneToOneField('ApplicantDetail', on_delete=models.CASCADE)
    registration_required_for = models.JSONField(default=list, blank=True)  # Categories of Single Use Plastics
    registration_required_for_other = models.JSONField(default=list, blank=True)  # Categories for Other Plastics
    plain_plastic_sheets_for_food_wrapping = models.JSONField(default=list, blank=True, null=True)  # Additional Options
    packaging_items = models.JSONField(default=list, blank=True, null=True)  # Additional Packaging Items
    consumption = models.CharField(max_length=100, blank=True, null=True)  # Consumption (Kg per Day)
    provision_waste_disposal_bins = models.CharField(
        max_length=3, choices=[('Yes', 'Yes'), ('No', 'No')], default='No'
    )  # Provision of Waste Disposal Bins
    no_of_waste_disposable_bins = models.PositiveIntegerField(blank=True, null=True)  # Number of Waste Disposal Bins
    segregated_plastics_handed_over_to_registered_recyclers = models.CharField(
        max_length=3, choices=[('Yes', 'Yes'), ('No', 'No')], default='No'
    )  # Segregated Plastics handed over to recyclers
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True,)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='consumercreatedby')

    registration_required_for_other_other_text = models.CharField(max_length=1024, blank=True, null=True)

    def __str__(self):
        return self.applicant.first_name


class Collector(models.Model):
    # Categories of Single Use Plastics
    applicant = models.OneToOneField(ApplicantDetail, on_delete=models.CASCADE, blank=True, null=True, )
    registration_required_for = models.JSONField(
        blank=True,
        null=True,
        help_text="Categories of Single Use Plastics (e.g., ['Carry bags', 'Packaging except food'])"
    )

    # Categories for Other Plastics
    registration_required_for_other = models.JSONField(
        blank=True,
        null=True,
        help_text="Categories for Other Plastics (e.g., ['Plastic Utensils', 'PET Bottles'])"
    )

    # Source of Disposal
    selected_categories = models.JSONField(
        blank=True,
        null=True,
        help_text=(
            "Source of Disposal, with details for each category. "
            "Example: [{'category': 'Recycler', 'address': '123 Street Name'}, {'category': 'Landfill Site', 'address': '456 Another St'}]"
        )
    )

    # Collection details
    total_capacity_value = models.FloatField(
        blank=True,
        null=True,
        help_text="Collection in Kg per day"
    )
    number_of_vehicles = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Number of vehicles for collection"
    )
    number_of_persons = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Number of persons for collection"
    )
    registration_required_for_other_other_text = models.CharField(max_length=1024, blank=True, null=True)

    # Metadata
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='collectorcreatedby')
    
    def __str__(self):
        return f"Collector ID: {self.id}, Collection Capacity: {self.total_capacity_value} Kg/day"


class Recycler(models.Model):
    applicant = models.OneToOneField(ApplicantDetail, on_delete=models.CASCADE)
    selected_categories = models.JSONField(default=list)  # Stores categories and their waste details
    plastic_waste_acquired_through = models.JSONField(
        default=list,  # Default to an empty list
        blank=True
    )

    has_adequate_pollution_control_systems = models.CharField(
        max_length=10,
        choices=[('Yes', 'Yes'), ('No', 'No')],
        default='No'
    )

    pollution_control_details = models.TextField(blank=True, null=True)

    registration_required_for_other_other_text = models.CharField(max_length=1024, blank=True, null=True)

    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='recyclercreatedby')
    
    def __str__(self):
        return self.applicant.first_name


class ApplicationAssignment(models.Model):
    applicant = models.ForeignKey(ApplicantDetail, on_delete=models.CASCADE, related_name='applicationassignment')
    assigned_group = models.CharField(max_length=100, null=True, choices=USER_GROUPS)
    remarks = models.TextField(null=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True,
                                   related_name='applicationassignmentupdatedby')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True,
                                   related_name='applicationassignmentcreatedby')

    def __str__(self):
        return self.applicant.first_name

    class Meta:
        indexes = [
            models.Index(fields=['applicant'], name='idx_applicant_assignment'),
            models.Index(fields=['assigned_group'], name='idx_assigned_group_assignment'),
            models.Index(fields=['assigned_group', 'created_by'], name='idx_group_created_assignment'),
        ]

def upload_to_with_uuid(instance, filename):
    """
    Generates a unique filename by prepending a UUID to the original filename.
    """
    original_name, ext = os.path.splitext(filename)  # Separate the original name and extension
    unique_filename = f"{uuid.uuid4()}_{original_name}{ext}"  # Prepend UUID and keep original name
    return os.path.join('media/documents/', unique_filename)

class ApplicantDocuments(models.Model):
    applicant = models.ForeignKey(ApplicantDetail, on_delete=models.CASCADE, related_name='applicationdocument')
    document = models.FileField(upload_to=upload_to_with_uuid)  # Use custom upload_to
    document_description = models.CharField(max_length=255)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True,
                                   related_name='applicationdocumentupdatedby')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True,
                                   related_name='applicationdocumentcreatedby')

    def __str__(self):
        return self.applicant.first_name

    class Meta:
        indexes = [
            models.Index(fields=['applicant'], name='idx_document_applicant'),
            models.Index(fields=['created_by'], name='idx_document_created_by'),
        ]


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']


class PSIDTracking(models.Model):
    # Input data fields
    applicant = models.ForeignKey('ApplicantDetail', on_delete=models.CASCADE, related_name='psid_tracking', null=True, blank=True)
    dept_transaction_id = models.CharField(max_length=50)
    due_date = models.DateField()
    expiry_date = models.DateTimeField()
    amount_within_due_date = models.DecimalField(max_digits=10, decimal_places=2)
    amount_after_due_date = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    consumer_name = models.CharField(max_length=255)
    mobile_no = models.CharField(max_length=15)
    cnic = models.CharField(max_length=13)
    email = models.EmailField(null=True, blank=True)
    district_id = models.IntegerField()
    amount_bifurcation = JSONField()  # Stores bifurcation data as JSON

    # Response data fields
    consumer_number = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="PSID")
    status = models.CharField(max_length=50, default="Pending")
    message = models.TextField(null=True, blank=True)

    # New fields for payment details
    payment_status = models.CharField(max_length=10, default="UNPAID")  # UNPAID or PAID
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    paid_date = models.DateField(null=True, blank=True)
    paid_time = models.TimeField(null=True, blank=True)
    bank_code = models.CharField(max_length=10, null=True, blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PSID {self.consumer_number or 'Pending'} - {self.dept_transaction_id}"

class ApplicantFieldResponse(models.Model):
    applicant = models.ForeignKey('ApplicantDetail', on_delete=models.CASCADE, related_name='field_responses')
    field_key = models.CharField(max_length=255)  # Key from `keyToTitleMapping`
    response = models.CharField(max_length=3, choices=[('Yes', 'Yes'), ('No', 'No')], default='Yes')
    comment = models.TextField(null=True, blank=True)  # Only populated if response is 'No'
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.field_key} - {self.response}"

class ApplicantManualFields(models.Model):
    applicant = models.OneToOneField(
        ApplicantDetail,
        on_delete=models.CASCADE,
        related_name='manual_fields'
    )
    # Latitude & Longitude
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    # Producer-related Fields
    list_of_products = models.TextField(null=True, blank=True)
    list_of_by_products = models.TextField(null=True, blank=True)
    raw_material_imported = models.TextField(null=True, blank=True)
    seller_name_if_raw_material_bought = models.CharField(max_length=255, null=True, blank=True)
    self_import_details = models.TextField(null=True, blank=True)
    raw_material_utilized = models.TextField(null=True, blank=True)
    compliance_thickness_75 = models.CharField(
        max_length=3,
        choices=[('Yes', 'Yes'), ('No', 'No')],
        null=True,
        blank=True
    )
    valid_consent_permit_building_bylaws = models.CharField(
        max_length=3,
        choices=[('Yes', 'Yes'), ('No', 'No')],
        null=True,
        blank=True
    )
    stockist_distributor_list = models.TextField(null=True, blank=True)

    # Consumer-related Field
    procurement_per_day = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Procurement in Kg per day"
    )

    # Recycler-related Fields
    no_of_workers = models.PositiveIntegerField(null=True, blank=True)
    labor_dept_registration_status = models.CharField(
        max_length=3,
        choices=[('Yes', 'Yes'), ('No', 'No')],
        null=True,
        blank=True
    )
    occupational_safety_and_health_facilities = models.TextField(null=True, blank=True)
    adverse_environmental_impacts = models.TextField(null=True, blank=True)

    # Optional Timestamps / Audit Fields
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='applicantmanualfields_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='applicantmanualfields_updated'
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Manual Fields for {self.applicant} (ID: {self.id})"

class ApplicantFee(models.Model):
    applicant = models.ForeignKey(ApplicantDetail, on_delete=models.CASCADE, related_name="applicantfees")
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_settled = models.BooleanField(default=False)  # Indicates if the fee is settled
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reason = models.TextField(blank=True, null=True)  # Reason or purpose for the fee (optional)

    class Meta:
        ordering = ['-created_at']  # Order by latest fee first

    def __str__(self):
        return f"Fee for {self.applicant} - Rs. {self.fee_amount}"

    class Meta:
        indexes = [
            models.Index(fields=['applicant'], name='idx_fee_applicant'),
            models.Index(fields=['is_settled'], name='idx_fee_is_settled'),
        ]

class ServiceConfiguration(models.Model):
    service_name = models.CharField(max_length=100, unique=True)
    base_url = models.URLField(help_text="Base endpoint of the service")
    auth_endpoint = models.URLField(help_text="Authentication endpoint")
    generate_psid_endpoint = models.URLField(help_text="PSID generation endpoint")
    transaction_status_endpoint= models.URLField(help_text="Transaction Status endpoint", null=True, blank=True)
    # If you also store credentials
    client_id = models.CharField(max_length=200)
    client_secret = models.CharField(max_length=500)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.service_name

class ExternalServiceToken(models.Model):
    service_name =  models.CharField(max_length=100)
    access_token = models.TextField()
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_expired(self):
        # Give a little buffer (e.g. 30 seconds) to account for clock skew
        return timezone.localtime() > self.expires_at
    
class ApiLog(models.Model):
    """
    Stores metadata about API calls made by our system, including request/response data.
    """
    service_name = models.CharField(max_length=100)
    endpoint = models.CharField(max_length=500)
    request_data = models.JSONField(null=True, blank=True)
    response_data = models.JSONField(null=True, blank=True)
    status_code = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.service_name} - {self.endpoint} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"