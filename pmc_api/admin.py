from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm

# Unregister default admin for User model
admin.site.unregister(User)

from .models import (
    TblDivisions,
    TblDistricts,
    TblTehsils,
    ApiLog,
    AuditLog,
    
    ApplicantDetail,
    ApplicationSubmitted,
    BusinessProfile,
    Producer,
    Consumer,
    Collector,
    Recycler,
    ApplicationAssignment,
    ApplicantDocuments,
    UserProfile,
    PSIDTracking,
    ApplicantFieldResponse,
    ApplicantManualFields,
    ApplicantFee,
    ServiceConfiguration,
    ExternalServiceToken,
    License,
    InspectionReport,
    DistrictPlasticCommitteeDocument,
    AccessLog,
    )


from django import forms
class CustomUserChangeForm(forms.ModelForm):
    password_plain = forms.CharField(
        label="New Password",
        required=False,
        widget=forms.PasswordInput,
        help_text="Leave blank to keep the current password."
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password_plain')
        if password:
            user.set_password(password)  # ✅ secure hashing
        if commit:
            user.save()
        return user

@admin.register(TblDivisions)
class TblDivisionsAdmin(admin.ModelAdmin):
    list_display = ['division_id', 'division_name', 'division_code']
    search_fields = ['division_name', 'division_code']
    ordering = ['division_name']

@admin.register(TblDistricts)
class TblDistrictsAdmin(admin.ModelAdmin):
    list_display = ['district_id', 'district_name', 'division', 'district_code', 'short_name']
    list_filter = ['division']
    search_fields = ['district_name', 'district_code', 'short_name']
    ordering = ['district_name']

@admin.register(TblTehsils)
class TblTehsilsAdmin(admin.ModelAdmin):
    list_display = ['tehsil_id', 'tehsil_name', 'tehsil_code', 'district', 'division']
    list_filter = ['district', 'division']
    search_fields = ['tehsil_name', 'tehsil_code']
    ordering = ['tehsil_name']

@admin.register(ApiLog)
class ApiLogAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'service_name', 'endpoint', 'status_code']
    list_filter = ['service_name', 'status_code']
    search_fields = ['service_name', 'endpoint', 'status_code']
    ordering = ['-created_at']

@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = (
        'timestamp',
        'get_user_display',
        'model_name',
        'object_id',
        'method',
        'ip_address',
        'endpoint',
    )
    list_filter = ('model_name', 'method', 'timestamp')
    search_fields = ('user__username', 'model_name', 'object_id', 'endpoint', 'ip_address')

    ordering = ['-timestamp']

    def get_user_display(self, obj):
        if obj.user:
            return f"{obj.user.username} ({obj.user.email})"
        return "Anonymous"

    get_user_display.short_description = 'User'


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'model_name', 'object_id', 'ip_address')
    search_fields = ('user__username', 'model_name', 'action', 'ip_address')
    list_filter = ('action', 'timestamp')
    
@admin.register(ApplicantDetail)
class ApplicantDetailAdmin(SimpleHistoryAdmin):
    list_display = [field.name for field in ApplicantDetail._meta.fields]

@admin.register(ApplicationSubmitted)
class ApplicationSubmittedAdmin(SimpleHistoryAdmin):
    list_display = [field.name for field in ApplicationSubmitted._meta.fields]

@admin.register(BusinessProfile)
class BusinessProfileAdmin(SimpleHistoryAdmin):
    list_display = [field.name for field in BusinessProfile._meta.fields]

@admin.register(Producer)
class ProducerAdmin(SimpleHistoryAdmin):
    list_display = [field.name for field in Producer._meta.fields]

@admin.register(Consumer)
class ConsumerAdmin(SimpleHistoryAdmin):
    list_display = [field.name for field in Consumer._meta.fields]

@admin.register(Collector)
class CollectorAdmin(SimpleHistoryAdmin):
    list_display = [field.name for field in Collector._meta.fields]

@admin.register(Recycler)
class RecyclerAdmin(SimpleHistoryAdmin):
    list_display = [field.name for field in Recycler._meta.fields]

@admin.register(ApplicationAssignment)
class ApplicationAssignmentAdmin(SimpleHistoryAdmin):
    list_display = [field.name for field in ApplicationAssignment._meta.fields]

@admin.register(ApplicantDocuments)
class ApplicantDocumentsAdmin(SimpleHistoryAdmin):
    list_display = [field.name for field in ApplicantDocuments._meta.fields]

@admin.register(UserProfile)
class UserProfileAdmin(SimpleHistoryAdmin):
    list_display = [field.name for field in UserProfile._meta.fields]

@admin.register(PSIDTracking)
class PSIDTrackingAdmin(SimpleHistoryAdmin):
    list_display = [field.name for field in PSIDTracking._meta.fields]

@admin.register(ApplicantFieldResponse)
class ApplicantFieldResponseAdmin(SimpleHistoryAdmin):
    list_display = [field.name for field in ApplicantFieldResponse._meta.fields]

@admin.register(ApplicantManualFields)
class ApplicantManualFieldsAdmin(SimpleHistoryAdmin):
    list_display = [field.name for field in ApplicantManualFields._meta.fields]

@admin.register(ExternalServiceToken)
class ExternalServiceTokenAdmin(SimpleHistoryAdmin):
    list_display = [field.name for field in ExternalServiceToken._meta.fields]

@admin.register(License)
class LicenseAdmin(SimpleHistoryAdmin):
    list_display = [field.name for field in License._meta.fields]
    
@admin.register(InspectionReport)
class InspectionReportAdmin(SimpleHistoryAdmin):
    list_display = [field.name for field in InspectionReport._meta.fields]

@admin.register(DistrictPlasticCommitteeDocument)
class DistrictPlasticCommitteeDocumentAdmin(SimpleHistoryAdmin):
    list_display = [field.name for field in DistrictPlasticCommitteeDocument._meta.fields]

@admin.register(ApplicantFee)
class ApplicantFeeAdmin(SimpleHistoryAdmin):
    list_display = [field.name for field in ApplicantFee._meta.fields]

@admin.register(ServiceConfiguration)
class ServiceConfigurationAdmin(SimpleHistoryAdmin):
    list_display = [field.name for field in ServiceConfiguration._meta.fields]

# Register User with history support
@admin.register(User)
class UserAdmin(SimpleHistoryAdmin):
    # form = CustomUserChangeForm
    list_display = [
        field.name for field in User._meta.fields 
        if field.name != 'password'  # 👈 Exclude password field
    ]
    search_fields = ['username', 'first_name', 'last_name', 'email']
    
    
class UpdateUser(User):
    class Meta:
        proxy = True
        app_label = 'auth'
        verbose_name = "Set User New Password"
        verbose_name_plural = "Set User New Password"

@admin.register(UpdateUser)
class UpdateUserAdmin(SimpleHistoryAdmin):
    form = CustomUserChangeForm
    list_display = [
        field.name for field in UpdateUser._meta.fields 
        if field.name != 'password'
    ]
    search_fields = ['username', 'first_name', 'last_name', 'email']