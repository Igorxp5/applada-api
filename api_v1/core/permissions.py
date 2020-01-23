import rest_framework.permissions

from django.utils.translation import ugettext as _


class IsAuthenticated(rest_framework.permissions.IsAuthenticated):
    pass


class IsOwnerUser(rest_framework.permissions.BasePermission):
    """
    Object-level permission to only allow only 
    the user himself to edit his profile.
    """
    message = _('You do not have permission to perform this action.')

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in rest_framework.permissions.SAFE_METHODS:
            return True

        return obj == request.user


class IsOwnerOrReadOnly(rest_framework.permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """
    message = _('You do not have permission to perform this action.')

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in rest_framework.permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return obj.owner == request.user


class IsMatchSubscriptionUserOrReadOnly(rest_framework.permissions.BasePermission):
    """
    Object-level permission to only allow only 
    the user himself to edit his profile.
    """
    message = _('You do not have permission to perform this action.')

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in rest_framework.permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return obj.user == request.user
