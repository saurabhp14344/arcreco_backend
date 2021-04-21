from rest_framework import generics
from .models import UserProfile
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
import requests
from .serializers import UserProfileSerializer, UpdateUserProfileSerializer, UpdateUserProfilePictureSerializer
from . import s3_upload
from arcreco import settings


class UserCreateAPIView(generics.CreateAPIView):
    """Create a profile view"""

    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data.get('name')
            serializer.save()
            return Response({
                'status': 'success',
                'message': f"hello {name}"
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileChangeAPIView(generics.RetrieveAPIView, generics.UpdateAPIView):
    """update user profile"""

    serializer_class = UpdateUserProfileSerializer

    queryset = UserProfile.objects.all()
    permission_classes = (IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': 'success', 'message': 'profile updated'}, status=status.HTTP_200_OK)


class ChangeProfilePictureView(generics.UpdateAPIView):
    """Update user profile picture"""
    serializer_class = UpdateUserProfilePictureSerializer

    queryset = UserProfile.objects.all()
    permission_classes = (IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user, data=request.data)
        if serializer.is_valid():
            # file = serializer.validated_data.get('profile_pic')
            # s3_image_path = s3_upload.create_presigned_post(key=file)
            # post_url = s3_image_path['url']
            # data = s3_image_path['fields']
            # response = requests.post(url=post_url, data=data, files={'file': file})
            # upload_to_s3 = 'https://%s.s3.amazonaws.com/%s' % (settings.AWS_STORAGE_BUCKET_NAME, file)
            # serializer.validated_data['profile_pic'] = upload_to_s3
            serializer.save()
            if serializer.data:
                return Response({
                    'status': 'success',
                    'profile_url': serializer.data['profile_pic']
                }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginApiView(ObtainAuthToken):
    """Handle creating user authentication"""
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class UserProfileView(generics.ListAPIView):
    """Get a profile view"""

    permission_classes = (IsAuthenticated,)
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        return UserProfile.objects.filter(id=self.request.user.id)
