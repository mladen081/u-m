# accounts/permissions.py

from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    """
    Allows access only to admin users.
    """
    message = "Only admin users can perform this action."
    
    def has_permission(self, request, view):
        return (
            request.user 
            and request.user.is_authenticated 
            and request.user.is_admin
        )


class IsOwnerOrAdmin(BasePermission):
    """
    Object-level permission to only allow owners of an object or admins to edit it.
    Assumes the model instance has an `user` or `owner` attribute.
    """
    message = "You must be the owner or an admin to perform this action."
    
    def has_object_permission(self, request, view, obj):
        # Admin can do anything
        if request.user.is_admin:
            return True
        
        # Check if object has 'user' or 'owner' attribute
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        
        return False


class IsAuthenticatedUser(BasePermission):
    """
    Allows access only to authenticated regular users (not admins).
    Useful if you want to restrict certain actions to non-admin users only.
    """
    message = "Only authenticated regular users can perform this action."
    
    def has_permission(self, request, view):
        return (
            request.user 
            and request.user.is_authenticated 
            and request.user.role == request.user.Role.USER
        )