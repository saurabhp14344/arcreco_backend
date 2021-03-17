from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserContactUsApiView

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path(r'contact_us', UserContactUsApiView.as_view()),
]