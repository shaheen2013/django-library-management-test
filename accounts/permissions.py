from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Permission to check if user is an admin.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.is_staff or request.user.role == 'admin')
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to allow users to edit their own profile or admins to edit any profile.
    """
    def has_object_permission(self, request, view, obj):
        # Admin users have full access
        if request.user.is_staff or request.user.role == 'admin':
            return True
        
        # Users can only access their own profile
        return obj == request.user


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission to allow anyone to read, but only owner to edit.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        return obj.user == request.user


