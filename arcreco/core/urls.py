from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserCreateAPIView, UserProfileChangeAPIView, ChangeProfilePictureView, UserProfileView, UserAddAPIView, ChangePasswordView, CompanyLogoView
from rest_framework_simplejwt import views as jwt_views

router = DefaultRouter()


urlpatterns = [
    path('', include(router.urls)),
    path(r'signup', UserCreateAPIView.as_view()),
    path(r'users', UserAddAPIView.as_view()),
    path(r'change_password', ChangePasswordView.as_view()),
    path(r'user_profile/', UserProfileView.as_view()),
    path(r'edit/', UserProfileChangeAPIView.as_view(), name='changeProfile'),
    path('login/', jwt_views.TokenObtainPairView.as_view()),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view()),
    path(r'profile_pic/', ChangeProfilePictureView.as_view(), name='ChangeProfilePicture'),
    path(r'logo', CompanyLogoView.as_view(), name='ChangeCompanyLogo'),
]