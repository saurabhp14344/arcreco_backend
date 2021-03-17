from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import UserContactUsSerializer
from .models import ContactUs


class UserContactUsApiView(generics.CreateAPIView):
    """Create user address"""
    permission_classes = (IsAuthenticated,)
    queryset = ContactUs.objects.all()
    serializer_class = UserContactUsSerializer

    def perform_create(self, serializer):
        """Set the user profile address"""
        serializer.save(user_profile=self.request.user)