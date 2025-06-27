from django.urls import path
from rest_framework.routers import DefaultRouter

from .controllers.application_receipt import ApplicationReceiptPDFView
from .controllers.bank_chalan import BankChalanPDFView, VerifyChalanQRCodeView, PingView
from .controllers.license import LicensePDFView, LicenseByUserView
from .controllers.pitb import plmis_token_view, payment_intimation_view, GeneratePsid, CheckPSIDPaymentStatus
from .controllers.reports import ReportAPIView, ReportFeeAPIView, ExportApplicantDetailsToExcelAPIView, \
    ApplicantFeeReportExcel
from .views import ApplicantDetailViewSet, BusinessProfileViewSet, PlasticItemsViewSet, ProductsViewSet, \
    ByProductsViewSet, ProducerViewSet, RawMaterialViewSet, DistrictViewSet, DistrictGEOMViewSet, TehsilViewSet, \
    UserGroupsViewSet, ApplicationAssignmentViewSet, FetchStatisticsViewSet, FetchStatisticsDOViewSet, generate_license_pdf, \
    ApplicantDocumentsViewSet, download_latest_document, RecyclerViewSet, ConsumerViewSet, CollectorViewSet, \
    ApplicantStatisticsView, download_file, download_file2, ApplicantFieldResponseViewSet, ApplicantManualFieldsViewSet, \
    ApplicantAlertsView, ApplicantDetailMainListViewSet, ApplicantDetailMainDOListViewSet, \
    TrackApplicationView, MISApplicantStatisticsView, ApplicantLocationViewSet, DistrictPlasticStatsViewSet, DistrictByLatLonSet, \
    InspectionReportViewSet, DistrictPlasticCommitteeDocumentViewSet, CompetitionRegistrationViewSet, generate_courier_label, \
    confiscation_lookup
from .idm_views import districts_club_counts, clubs_geojson_all, ClubGeoJSONViewSet

router = DefaultRouter()
router.register(r'applicant-detail', ApplicantDetailViewSet, basename='applicant-detail')
router.register(r'applicant-detail-main-list', ApplicantDetailMainListViewSet, basename='applicant-detail-main-list')
router.register(r'applicant-detail-main-do-list', ApplicantDetailMainDOListViewSet, basename='applicant-detail-main-do-list')
router.register(r'business-profiles', BusinessProfileViewSet, basename='business-profile')
router.register(r'plastic-items', PlasticItemsViewSet, basename='plastic-items')
router.register(r'products', ProductsViewSet, basename='products')
router.register(r'by-products', ByProductsViewSet, basename='by-products')
router.register(r'producers', ProducerViewSet, basename='producers')
router.register(r'consumers', ConsumerViewSet, basename='consumers')
router.register(r'collectors', CollectorViewSet, basename='collectors')
router.register(r'recyclers', RecyclerViewSet, basename='recyclers')
router.register(r'applicant-documents', ApplicantDocumentsViewSet, basename='applicant-documents')
router.register(r'raw-materials', RawMaterialViewSet, basename='raw-materials')
# router.register(r'divisions', DivisionViewSet, basename='division')
router.register(r'districts', DistrictViewSet, basename='district')
router.register(r'districts-public', DistrictGEOMViewSet, basename='district-public')
router.register(r'applicant-location-public', ApplicantLocationViewSet, basename='applicant-location-public')
router.register(r'tehsils', TehsilViewSet, basename='tehsil')
router.register(r'user-groups', UserGroupsViewSet, basename='user-groups'),
router.register(r'application-assignment', ApplicationAssignmentViewSet, basename='ApplicationAssignment')
router.register(r'fetch-statistics-view-groups', FetchStatisticsViewSet, basename='FetchStatisticsView')
router.register(r'fetch-statistics-do-view-groups', FetchStatisticsDOViewSet, basename='FetchStatisticsLSOView')
router.register(r'field-responses', ApplicantFieldResponseViewSet, basename='field-responses')
router.register(r'manual-fields', ApplicantManualFieldsViewSet, basename='manual-fields')
router.register(r'mis-district-plastic-stats', DistrictPlasticStatsViewSet, basename='mis-district-plastic-stats')
router.register(r'inspection-report', InspectionReportViewSet, basename='inspection-report')
router.register(r'inspection-report-cached', InspectionReportViewSet, basename='inspection-report-cached')
router.register(r'district-documents', DistrictPlasticCommitteeDocumentViewSet, basename="district-documents")
router.register(r'idm_clubs', ClubGeoJSONViewSet, basename='clubs')
router.register(r'competition/register', CompetitionRegistrationViewSet, basename='competition-registration')

urlpatterns = router.urls + [
    path('receipt-pdf/', ApplicationReceiptPDFView.as_view(), name='receipt-pdf'),
    path('chalan-pdf/', BankChalanPDFView.as_view(), name='chalan-pdf'),
    path('license-pdf/', LicensePDFView.as_view(), name='license-pdf'),
    path('license-by-user/', LicenseByUserView.as_view(), name='license-by-user'),
    path('verify-chalan/', VerifyChalanQRCodeView.as_view(), name='verify-chalan'),
    path('ping/', PingView.as_view(), name='Ping'),
    path("generate-license-pdf/", generate_license_pdf, name="generate_license_pdf"),
    path("download_latest_document/", download_latest_document, name="download_latest_document"),
    path('applicant-statistics/', ApplicantStatisticsView.as_view(), name='applicant-statistics'),
    path('mis-applicant-statistics/', MISApplicantStatisticsView.as_view(), name='mis-applicant-statistics'),
    path('media/<str:folder_name>/<str:file_name>/', download_file, name='download_file'),
    path('media/<str:folder_name>/<str:folder_name2>/<str:file_name>/', download_file2, name='download_file2'),
    path('applicant-alerts/', ApplicantAlertsView.as_view(), name='applicant-alerts'),
    path('DistrictByLatLon/', DistrictByLatLonSet.as_view(), name='DistrictByLatLonSet'),
    path('track-application/', TrackApplicationView.as_view(), name='track-application'),
    path('report/', ReportAPIView.as_view(), name='report'),
    path('psid-report/', ApplicantFeeReportExcel.as_view(), name='psid-report'),
    path('export-applicant/', ExportApplicantDetailsToExcelAPIView.as_view(), name='export-applicant'),
    path('report-fee/', ReportFeeAPIView.as_view(), name='report_fee'),
    path('generate-psid/', GeneratePsid.as_view(), name='generate-psid'),
    path('check-psid-status/', CheckPSIDPaymentStatus.as_view(), name='check-psid-status'),

    path('payment-intimation/', payment_intimation_view, name='payment-intimation'),
    path('plmis-token/', plmis_token_view, name='custom_token'),

    path("idm_districts-club-counts/", districts_club_counts, name="idm_districts_club_counts"),
    path("idm_clubs_geojson_all/", clubs_geojson_all, name="idm_clubs_geojson_all"),
    path('competition/generate-label/', generate_courier_label, name='generate-courier-label'),
    path("confiscation-lookup/", confiscation_lookup, name="confiscation-lookup"),

]