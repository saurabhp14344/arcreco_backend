from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserUploadFileApiView, MatchFilesApiView

router = DefaultRouter()


urlpatterns = [
    path('', include(router.urls)),
    path(r'upload/<int:pk>/', UserUploadFileApiView.as_view(), name='Upload user files'),
    path(r'recon/', MatchFilesApiView.as_view(), name='Match User Files'),
]