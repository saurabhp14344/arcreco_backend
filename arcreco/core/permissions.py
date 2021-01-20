from rest_framework import permissions


class UpdateOwnProfile(permissions.BasePermission):
    """Allow user to edit profile"""

    def has_object_permission(self, request, view, obj):
        """check user has permission or not"""
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.id == request.user.id
