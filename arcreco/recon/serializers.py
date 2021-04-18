from rest_framework import serializers
from django.db.models import Q
from .models import TotalReconcile, UploadFiles


class UserUploadFileSerializer(serializers.ModelSerializer):
    """upload file serializer"""

    class Meta:
        model = UploadFiles
        fields = ('id', 'user_profile', 'name', 'file', 'type', 'created_date')
        extra_kwargs = {'user_profile': {'read_only': True},
                        'name': {'required': False},
                        'file': {'required': True},
                        'type': {'required': True},
                        }


class TotalReconcileSerializer(serializers.ModelSerializer):
    file1 = serializers.CharField(max_length=240)
    file2 = serializers.CharField(max_length=240)

    class Meta:
        model = TotalReconcile
        fields = ('name', 'sales_count', 'file1', 'file2',)
        extra_kwargs = {
            "name": {"required": False},
            "sales_count": {"required": False},
        }

    def create(self, **kwargs):
        if TotalReconcile.objects.filter(name__contains=kwargs.get('name')):
            pass
        else:
            obj = TotalReconcile.objects.create(
                user_profile=kwargs.get('profile'),
                name=kwargs.get('name'),
                sales_count=kwargs.get('sales_count'),
                reconcile_count=kwargs.get('reconcile_count'),
                ageing_count=kwargs.get('ageing_count'),
                start_date=str(kwargs.get('start_date')),
                end_date=str(kwargs.get('end_date'))
            )
            return obj


class ReportSerializer(serializers.Serializer):
    """pass file to get generate reports"""
    file = serializers.CharField(max_length=240, required=True)