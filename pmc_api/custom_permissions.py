from rest_framework.permissions import BasePermission

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
    
    
        # user = self.request.user
        # target_groups = {'LSO', 'LSM', 'DO', 'TL', 'MO', 'LSM2','DEO', 'Download License'}
        # user_groups = set(user.groups.values_list('name', flat=True))
        # matching_groups = user_groups.intersection(target_groups)

        
        # if matching_groups:
        #     return ApplicantDetail.objects.filter(assigned_group__in=matching_groups)