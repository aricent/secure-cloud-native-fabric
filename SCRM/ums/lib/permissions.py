"""
Here we've added scf custom Permission classes
we can use these classes as per our need
"""

from rest_framework import permissions


class SafeMethodsOnlyPermission(permissions.BasePermission):
    """Only can access non-destructive methods (like GET and HEAD)"""

    # def has_permission(self, request, view):
    #    return self.has_object_permission(request, view)

    def has_object_permission(self, request, view, obj=None):
        return request.method in permissions.SAFE_METHODS


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj.owner == request.user


class NotAnonymousPerm(permissions.BasePermission):
    def has_permission(self, request, view):
        # anon users cannot see anything
        if request.user.is_anonymous():
            return False
        return True


class SuperuserPerm(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser
