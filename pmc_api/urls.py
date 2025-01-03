from django.urls import path
from rest_framework.routers import DefaultRouter

from .controllers.application_receipt import ApplicationReceiptPDFView
from .controllers.bank_chalan import BankChalanPDFView, VerifyChalanQRCodeView, PingView
from .controllers.pitb import plmis_token_view, payment_intimation_view, GeneratePsid, CheckPSIDPaymentStatus
from .controllers.reports import ReportAPIView
from .views import ApplicantDetailViewSet, BusinessProfileViewSet, PlasticItemsViewSet, ProductsViewSet, \
    ByProductsViewSet, ProducerViewSet, RawMaterialViewSet, DistrictViewSet, TehsilViewSet, \
    UserGroupsViewSet, ApplicationAssignmentViewSet, FetchStatisticsViewSet, generate_license_pdf, \
    ApplicantDocumentsViewSet, download_latest_document, RecyclerViewSet, ConsumerViewSet, CollectorViewSet, \
    ApplicantStatisticsView, download_file, ApplicantFieldResponseViewSet, ApplicantManualFieldsViewSet, \
    ApplicantAlertsView, \
    ApplicantDetailMainListViewSet

router = DefaultRouter()
router.register(r'applicant-detail', ApplicantDetailViewSet, basename='applicant-detail')
router.register(r'applicant-detail-main-list', ApplicantDetailMainListViewSet, basename='applicant-detail-main-list')
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
router.register(r'tehsils', TehsilViewSet, basename='tehsil')
router.register(r'user-groups', UserGroupsViewSet, basename='user-groups'),
router.register(r'application-assignment', ApplicationAssignmentViewSet, basename='ApplicationAssignment')
router.register(r'fetch-statistics-view-groups', FetchStatisticsViewSet, basename='FetchStatisticsView')
router.register(r'field-responses', ApplicantFieldResponseViewSet, basename='field-responses')
router.register(r'manual-fields', ApplicantManualFieldsViewSet, basename='manual-fields')

urlpatterns = router.urls + [
    path('receipt-pdf/', ApplicationReceiptPDFView.as_view(), name='receipt-pdf'),
    path('chalan-pdf/', BankChalanPDFView.as_view(), name='chalan-pdf'),
    path('verify-chalan/', VerifyChalanQRCodeView.as_view(), name='verify-chalan'),
    path('ping/', PingView.as_view(), name='Ping'),
    path("generate-license-pdf/", generate_license_pdf, name="generate_license_pdf"),
    path("download_latest_document/", download_latest_document, name="download_latest_document"),
    path('applicant-statistics/', ApplicantStatisticsView.as_view(), name='applicant-statistics'),
    path('media/documents/<str:file_name>/', download_file, name='download_file'),
    path('applicant-alerts/', ApplicantAlertsView.as_view(), name='applicant-alerts'),
    path('report/', ReportAPIView.as_view(), name='report'),
    path('generate-psid/', GeneratePsid.as_view(), name='generate-psid'),
    path('check-psid-status/', CheckPSIDPaymentStatus.as_view(), name='check-psid-status'),
    
    path('payment-intimation/', payment_intimation_view, name='payment-intimation'),
    path('plmis-token/', plmis_token_view, name='custom_token'),
]
