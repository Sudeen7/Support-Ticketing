from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """
    Custom permission to only allow admin users to access the view.
    """
    def has_permission(self, request, view):
        return request.user and hasattr(request.user, 'profile') and request.user.profile.role == 'admin'

class IsSupport(permissions.BasePermission):
    """
    Custom permission to only allow support users to access the view.
    """
    def has_permission(self, request, view):
        return request.user and hasattr(request.user, 'profile') and request.user.profile.role == 'support'

class IsClient(permissions.BasePermission):
    """
    Custom permission to only allow client users to access the view.
    """
    def has_permission(self, request, view):
        return request.user and hasattr(request.user, 'profile') and request.user.profile.role == 'client'

class IsAdminOrSupport(permissions.BasePermission):
    """
    Custom permission to only allow admin or support users to access the view.
    """
    def has_permission(self, request, view):
        if not request.user or not hasattr(request.user, 'profile'):
            return False
        return request.user.profile.role in ['admin', 'support']

class IsTicketOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a ticket to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the ticket
        return obj.created_by == request.user

class IsTicketAssignee(permissions.BasePermission):
    """
    Custom permission to only allow assignees of a ticket to update it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the assignee of the ticket
        return obj.assigned_to == request.user