from rest_framework import permissions
from accounts.permissions import IsAdmin, IsSupport, IsClient, IsAdminOrSupport

class CanViewTicket(permissions.BasePermission):
    """
    Permission to check if user can view a ticket:
    - Admins can view all tickets
    - Support can view tickets assigned to them or unassigned
    - Clients can only view their own tickets
    """
    def has_object_permission(self, request, view, obj):
        if not request.user or not hasattr(request.user, 'profile'):
            return False
            
        # Admin can view all tickets
        if request.user.profile.role == 'admin':
            return True
            
        # Support can view tickets assigned to them or unassigned
        if request.user.profile.role == 'support':
            return obj.assigned_to == request.user or obj.assigned_to is None
            
        # Clients can only view their own tickets
        if request.user.profile.role == 'client':
            return obj.created_by == request.user
            
        return False

class CanUpdateTicket(permissions.BasePermission):
    """
    Permission to check if user can update a ticket:
    - Admins can update all tickets
    - Support can update tickets assigned to them
    - Clients can update their own tickets but with limited fields
    """
    def has_object_permission(self, request, view, obj):
        if not request.user or not hasattr(request.user, 'profile'):
            return False
            
        # Admin can update all tickets
        if request.user.profile.role == 'admin':
            return True
            
        # Support can update tickets assigned to them
        if request.user.profile.role == 'support':
            return obj.assigned_to == request.user
            
        # Clients can update their own tickets but with limited fields
        if request.user.profile.role == 'client':
            if obj.created_by != request.user:
                return False
                
            # Clients can only update title and description
            allowed_fields = {'title', 'description'}
            requested_fields = set(request.data.keys())
            return requested_fields.issubset(allowed_fields)
            
        return False

class CanDeleteTicket(permissions.BasePermission):
    """
    Permission to check if user can delete a ticket:
    - Admins can delete any ticket
    - Support cannot delete tickets
    - Clients can only delete their own tickets if they are still open
    """
    def has_object_permission(self, request, view, obj):
        if not request.user or not hasattr(request.user, 'profile'):
            return False
            
        # Admin can delete any ticket
        if request.user.profile.role == 'admin':
            return True
            
        # Support cannot delete tickets
        if request.user.profile.role == 'support':
            return False
            
        # Clients can only delete their own tickets if they are still open
        if request.user.profile.role == 'client':
            return obj.created_by == request.user and obj.status == 'open'
            
        return False

class CanCommentOnTicket(permissions.BasePermission):
    """
    Permission to check if user can comment on a ticket:
    - Admins can comment on any ticket
    - Support can comment on tickets assigned to them
    - Clients can comment on their own tickets
    """
    def has_permission(self, request, view):
        return request.user and hasattr(request.user, 'profile')
        
    def has_object_permission(self, request, view, obj):
        if not request.user or not hasattr(request.user, 'profile'):
            return False
            
        # Admin can comment on any ticket
        if request.user.profile.role == 'admin':
            return True
            
        # Support can comment on tickets assigned to them
        if request.user.profile.role == 'support':
            return obj.ticket.assigned_to == request.user
            
        # Clients can comment on their own tickets
        if request.user.profile.role == 'client':
            return obj.ticket.created_by == request.user
            
        return False