from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import UserContactUsSerializer
from .models import ContactUs


class UserContactUsApiView(generics.CreateAPIView):
    """Create user address"""
    permission_classes = (IsAuthenticated,)
    queryset = ContactUs.objects.all()
    serializer_class = UserContactUsSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(user_profile=self.request.user)
            return Response({'status': 'success', 'data': serializer.data})
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
