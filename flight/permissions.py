from rest_framework import permissions


class IsGetOrIsAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        # allow all GET requests
        if request.method == 'GET':
            return True

        # Otherwise, only allow admin requests
        return request.user and request.user.is_staff


class IsAdminOrIsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        """
        Determines if a user should see or edit a flight reservation
]       """
        user = request.user
        if user:
            return user.is_staff or obj.passenger == user

        return False
