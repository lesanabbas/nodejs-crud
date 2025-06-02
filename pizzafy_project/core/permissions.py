from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Custom permission to only allow admins to access the API
    """

    def has_permission(self, request, view):
        # Allow access only to Admin users
        return request.user.role == "Admin"


class IsCustomer(permissions.BasePermission):
    """
    Custom permission to only allow customers to access the API
    """

    # def has_permission(self, request, view):
    #     # Allow access only if the user has a 'Customer' role
    #     return bool(request.user and request.user.is_authenticated and request.user.role == "Customer")
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "Customer")
