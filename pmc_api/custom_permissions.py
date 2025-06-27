from rest_framework.permissions import BasePermission
from rest_framework import exceptions

class IsOwnerOrAdmin(BasePermission):
    """
    Custom permission to allow only the creator or admin to modify a record.
    """

    def has_object_permission(self, request, view, obj):
        # Allow superusers/admins to access
        # return True
        print("Its checking security:")
        if request.user.is_superuser:
            return True

        # Get the groups the user belongs to
        user_groups = set(request.user.groups.values_list('name', flat=True))  # Extract group names as a set

        # Check if the user has any group assigned
        if user_groups:
            print("User has group(s) assigned:", user_groups)
            return True

        # Check if the object has a 'created_by' attribute and compare it to the user's ID
        creator_id = getattr(obj, 'created_by_id', None)  # Use '_id' if the field stores the user ID
        assigned_group = getattr(obj, 'assigned_group', None)  # The assigned group of the object
        print('user assigned group:')
        print(assigned_group)
        # Get the groups the user belongs to
        user_groups = set(request.user.groups.values_list('name', flat=True))  # Extract group names as a set
        print('user groups')
        print(user_groups)
        # List of allowed groups

        # Allow access if the user is the creator, or their group is in the allowed groups, or the assigned group matches
        if creator_id == request.user.id or assigned_group in user_groups or creator_id == None:
            print('going to return true from authentication')
            return True

        # Deny access otherwise
        return False
    
class IsInAnalytics1Group(BasePermission):
    """
    Custom permission to allow access only to users in the 'Analytics1' group.
    """
    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if the user is part of the 'Analytics1' group
        if request.user.groups.filter(name='Analytics1').exists():
            return True
        
        # If the user is not in the required group, deny access
        raise exceptions.PermissionDenied("You do not have permission to access this resource.")

class IsInAnalytics2Group(BasePermission):
    """
    Custom permission to allow access only to users in the 'Analytics1' group.
    """
    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if the user is part of the 'Analytics1' group
        if request.user.groups.filter(name='Analytics2').exists() or request.user.groups.filter(name='Analytics').exists():
            return True
        
        # If the user is not in the required group, deny access
        raise exceptions.PermissionDenied("You do not have permission to access this resource.")
    
class IsInAnalytics3Group(BasePermission):
    """
    Custom permission to allow access only to users in the 'Analytics1' group.
    """
    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if the user is part of the 'Analytics1' group
        if request.user.groups.filter(name='Analytics3').exists():
            return True
        
        # If the user is not in the required group, deny access
        raise exceptions.PermissionDenied("You do not have permission to access this resource.")

class IsGroupExist(BasePermission):
    """
    Custom permission to allow access only to users in the 'Analytics1' group.
    """
    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if the user is part of the 'Analytics1' group
        if request.user.groups.exists():
            return True  # User is part of at least one group

        
        # If the user is not in the required group, deny access
        raise exceptions.PermissionDenied("You do not have permission to access this resource.")