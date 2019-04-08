from rest_framework import permissions


class IsGetOrIsAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        # allow all GET requests
        if request.method == 'GET':
            return True

        # Otherwise, only allow admin requests
        return request.user and request.user.is_staff
