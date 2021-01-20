from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserCreateAPIView, UserProfileChangeAPIView, ChangeProfilePictureView
from rest_framework_simplejwt import views as jwt_views

router = DefaultRouter()


urlpatterns = [
    path('', include(router.urls)),
    path(r'signup', UserCreateAPIView.as_view()),
    path(r'edit/<int:pk>/', UserProfileChangeAPIView.as_view(), name='changeProfile'),
    path('login/', jwt_views.TokenObtainPairView.as_view()),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view()),
    path(r'profile_pic/<int:pk>/', ChangeProfilePictureView.as_view(), name='ChangeProfilePicture'),
]