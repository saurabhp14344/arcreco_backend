from rest_framework import serializers
from . import models


class UserProfileSerializer(serializers.ModelSerializer):
    """user profile serializer"""

    class Meta:
        model = models.UserProfile
        fields = ('id', 'email', 'name', 'password', 'contact', 'company_name', 'last_name', 'designation')
        extra_kwargs = {
            'password': {
                'write_only': True,
                'style': {
                    'input_type': 'password'
                }
            },
            "contact": {"required": True}
        }

    def create(self, validated_data):
        """create and return new user"""

        user = models.UserProfile.objects.create_user(**validated_data)
        return user


class UpdateUserProfileSerializer(serializers.ModelSerializer):
    """Update user profile """
    class Meta:
        model = models.UserProfile
        fields = ('name', 'contact', 'last_name',)
        extra_kwargs = {
            "name": {"required": False},
            "contact": {"required": False},
            "last_name": {"required": False},
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