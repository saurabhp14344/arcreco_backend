from rest_framework import serializers
from .models import ContactUs


class UserContactUsSerializer(serializers.ModelSerializer):
    """contact us serializer"""
    class Meta:
        model = ContactUs
        fields = ('id', 'user_profile', 'name', 'email', 'contact', 'subject', 'desc',)
        extra_kwargs = {'user_profile': {'read_only': True},
                        'subject': {'required': True},
                        'desc': {'required': True},
                        }

        def create(self, validated_data):
            """create contactus information"""

            parking_detail = ContactUs.objects.create(**validated_data)
            return parking_detail
