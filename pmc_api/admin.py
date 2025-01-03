from django.contrib import admin

from .models import (
    TblDivisions,
    TblDistricts,
    TblTehsils,
    ApplicantDetail,
    BusinessProfile,
    PlasticItems,
    Products,
    ByProducts,
    Producer,
    RawMaterial,
    ServiceConfiguration,
    ExternalServiceToken,
    ApiLog,
    PSIDTracking
    )


admin.site.register(TblDivisions)
admin.site.register(TblDistricts)
admin.site.register(TblTehsils)
admin.site.register(ApplicantDetail)
admin.site.register(BusinessProfile)
admin.site.register(PlasticItems)
admin.site.register(Products)
admin.site.register(ByProducts)
admin.site.register(Producer)
admin.site.register(RawMaterial)
admin.site.register(ServiceConfiguration)
admin.site.register(ExternalServiceToken)
admin.site.register(ApiLog)
admin.site.register(PSIDTracking)
