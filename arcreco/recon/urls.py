from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserUploadFileApiView, MatchFilesApiView, TotalFilesApiView, AgeingReportApiView, ModePaymentReportApiView, SalesReportApiView, ExceptionReportApiView, SettlementReportApiView, TimeSettlementReport, GenerateReportDashboard

router = DefaultRouter()


urlpatterns = [
    path('', include(router.urls)),
    path(r'upload/', UserUploadFileApiView.as_view(), name='Upload user files'),
    path(r'recon/', MatchFilesApiView.as_view(), name='Match User Files'),
    path(r'filecount/', TotalFilesApiView.as_view()),
    path(r'ageing_report/', AgeingReportApiView.as_view()),
    path(r'mode_payment_report/', ModePaymentReportApiView.as_view()),
    path(r'sales_report/', SalesReportApiView.as_view()),
    path(r'exception_report/', ExceptionReportApiView.as_view()),
    path(r'settlement_report/', SettlementReportApiView.as_view()),
    path(r'time_settlement_report/', TimeSettlementReport.as_view()),
    path(r'generate_report_dashboard/', GenerateReportDashboard.as_view()),
]