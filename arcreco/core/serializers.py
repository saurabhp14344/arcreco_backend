from rest_framework import serializers
from . import models


class UserProfileSerializer(serializers.ModelSerializer):
    """user profile serializer"""
    f_name = serializers.CharField(source='name')
    l_name = serializers.CharField(source='last_name')
    mobile = serializers.CharField(source='contact')

    class Meta:
        model = models.UserProfile
        fields = ('id', 'email', 'f_name', 'password', 'mobile', 'company_name', 'l_name', 'designation')
        extra_kwargs = {
            'password': {
                'write_only': True,
                'style': {
                    'input_type': 'password'
                }
            },
            "mobile": {"required": True}
        }

    def create(self, validated_data):
        """create and return new user"""

        user = models.UserProfile.objects.create_user(**validated_data)
        return user


class UpdateUserProfileSerializer(serializers.ModelSerializer):
    """Update user profile """
    f_name = serializers.CharField(source='name')
    l_name = serializers.CharField(source='last_name')
    mobile = serializers.CharField(source='contact')

    class Meta:
        model = models.UserProfile
        fields = ('f_name', 'mobile', 'l_name', 'company_name', 'designation',)
        extra_kwargs = {
            "f_name": {"required": False},
            "mobile": {"required": False},
            "l_name": {"required": False},
            "company_name": {"required": False},
            "designation": {"required": False},
        }

    def update(self, instance, validated_data):
        for (key, value) in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class UpdateUserProfilePictureSerializer(serializers.ModelSerializer):
    """Update user profile """

    class Meta:
        model = models.UserProfile
        fields = ('profile_pic',)
        extra_kwargs = {
            "profile_pic": {"required": True},
        }


class AddNewUserProfileSerializer(serializers.ModelSerializer):
    """Add new user api"""
    f_name = serializers.CharField(source='name')
    l_name = serializers.CharField(source='last_name')
    mobile = serializers.CharField(source='contact')

    class Meta:
        model = models.UserProfile
        fields = ('id', 'email', 'f_name', 'mobile', 'l_name', 'designation', 'department', 'city', 'state', 'country')
        extra_kwargs = {
            "email": {"required": True},
            "f_name": {"required": True},
            "mobile": {"required": True},
            "l_name": {"required": True},
            "designation": {"required": True},
            "department": {"required": True},
            "city": {"required": True},
            "state": {"required": True},
            "country": {"required": True},
        }

    def create(self, validated_data):
        """create and return new user"""

        user = models.UserProfile.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        for (key, value) in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class CompanyLogoSerializer(serializers.ModelSerializer):
    """change company logo"""

    class Meta:
        model = models.UserCompanyLogo
        fields = ('logo',)
        extra_kwargs = {
            "logo": {"required": True},
        }

    def update(self, instance, validated_data):
        c_logo = models.UserCompanyLogo(users=instance, logo=validated_data.get('logo'))
        c_logo.save()
        return c_logo
