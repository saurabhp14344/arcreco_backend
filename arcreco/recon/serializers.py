from rest_framework import serializers
from . import models


class UserUploadFileSerializer(serializers.ModelSerializer):
    """upload file serializer"""

    class Meta:
        model = models.UploadFiles
        fields = ('id', 'user_profile', 'name', 'file', 'type', 'created_date')
        extra_kwargs = {'user_profile': {'read_only': True},
                        'name': {'required': False},
                        'file': {'required': True},
                        'type': {'required': True},
                        }


class MatchFilesSerializer(serializers.Serializer):
    """match files uploaded by users"""

    file1 = serializers.CharField(max_length=160)
    file2 = serializers.CharField(max_length=160)
