from rest_framework import permissions



class IsStaffOrNotAllowed(permissions.BasePermission):
    """
    dashboard permission check for staff Users .
    """

    def has_permission(self, request, view):
        return request.user.is_staff
    
    
class StaffNotAllowed(permissions.BasePermission):
    """
    permission check for regular Users .
    """

    def has_permission(self, request, view):
        return not request.user.is_staff