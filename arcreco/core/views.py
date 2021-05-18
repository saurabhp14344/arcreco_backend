from rest_framework import generics
from rest_framework_simplejwt.views import TokenObtainPairView
from django.core.mail import EmailMessage
from .models import UserProfile, UserCompanyLogo
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Q
from .serializers import UserProfileSerializer, UpdateUserProfileSerializer, UpdateUserProfilePictureSerializer, \
    AddNewUserProfileSerializer, ChangePasswordSerializer, CompanyLogoSerializer, TokenObtainPairPatchedSerializer
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
                'message': f"Hello {name}"
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
                    'profile_url': f"http://{request.get_host()}{serializer.data['profile_pic']}"
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


class UserAddAPIView(generics.ListAPIView, generics.CreateAPIView, generics.UpdateAPIView, generics.DestroyAPIView):
    """Add new profile by admin"""

    permission_classes = (IsAuthenticated, IsAdminUser,)
    serializer_class = AddNewUserProfileSerializer

    def get_queryset(self):
        word = self.request.query_params.get('q')
        queryset = UserProfile.objects.all()
        if word:
            queryset = queryset.filter(Q(name__icontains=word) | Q(email__icontains=word))
        return queryset

    def send_email(request, **kwargs):
        email = EmailMessage(
            settings.EMAIL_SUBJECT,
            f"Hello {kwargs.get('name')}, \nYou registered an account on portal.Find your credentials here:\n \nemail: {kwargs.get('email')} \npassword: arc!&@pa4527y \nyou can change your password click here: https://abc.com \n\nKind Regards, \nArcReco",
            settings.EMAIL_HOST_USER,
            [kwargs.get('email')]
        )
        email.send()

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data.get('name')
            serializer.save()
            data = {
                'name': name,
                'email': serializer.validated_data.get('email'),
                'contact': serializer.validated_data.get('mobile'),
            }
            self.send_email(**data)
            return Response({
                'status': 'success',
                'message': f"hello {name}, please check your mail for login credentials."
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            user = UserProfile.objects.get(id=request.data.get('id'))
        except:
            return Response({'status': 'failed', 'message': 'user not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': 'success', 'message': 'profile updated'}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        user_id = request.query_params.get('id')
        if user_id:
            try:
                user = UserProfile.objects.get(id=request.query_params.get('id'))
                user.delete()
                return Response({'status': 'success', 'message': 'user deleted'}, status=status.HTTP_204_NO_CONTENT)
            except:
                return Response({'status': 'failed', 'message': 'user not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'id': ['This field is required.']}, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(generics.UpdateAPIView):
    """
    An endpoint for changing password.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        user_obj = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not user_obj.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            user_obj.set_password(serializer.data.get("new_password"))
            user_obj.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompanyLogoView(generics.UpdateAPIView):
    """Update user profile picture"""
    serializer_class = CompanyLogoSerializer

    queryset = UserCompanyLogo.objects.all()
    permission_classes = (IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            if serializer.data:
                return Response({
                    'status': 'success',
                    'logo': f"http://{request.get_host()}{str(serializer.data['logo'])}"
                }, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenObtainPairPatchedView(TokenObtainPairView):
    """
    Takes a set of user credentials and returns an access and refresh JSON web
    token pair to prove the authentication of those credentials.
    """
    serializer_class = TokenObtainPairPatchedSerializer

    token_obtain_pair = TokenObtainPairView.as_view()


class GetUserByAdminView(generics.ListAPIView):
    """Get single user details by admin on id"""
    permission_classes = (IsAuthenticated, IsAdminUser,)
    queryset = UserProfile.objects.all()

    def get(self, request, *args, **kwargs):
        user_id = request.query_params.get('id')
        if user_id:
            try:
                user = UserProfile.objects.get(id=request.query_params.get('id'))
                data = {
                    'f_name': user.name,
                    'l_name': user.last_name,
                    'contact': user.contact,
                    'email': user.email,
                    'company_name': user.company_name,
                    'designation': user.designation,
                    'department': user.department,
                    'city': user.city,
                    'state': user.state,
                    'country': user.country
                }
                return Response({'status': 'success', 'data': data})
            except:
                return Response({'status': 'failed', 'message': 'user not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'id': ['This field is required.']}, status=status.HTTP_400_BAD_REQUEST)