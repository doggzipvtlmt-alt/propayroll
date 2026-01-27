from rest_framework.permissions import BasePermission


class RolePermission(BasePermission):
    required_role = None

    def has_permission(self, request, view):
        if not request.user or not getattr(request.user, 'is_authenticated', False):
            return False
        if self.required_role is None:
            return True
        return request.user.role == self.required_role


class RoleAnyPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not getattr(request.user, 'is_authenticated', False):
            return False
        roles = getattr(view, 'allowed_roles', set())
        return request.user.role in set(roles)


class MakerOnly(BasePermission):
    allowed_roles = {'MAKER', 'SUPERUSER'}

    def has_permission(self, request, view):
        if not request.user or not getattr(request.user, 'is_authenticated', False):
            return False
        return request.user.role in self.allowed_roles


class HROnly(RolePermission):
    required_role = 'HR'


class MDOnly(RolePermission):
    required_role = 'MD'


class FinanceOnly(RolePermission):
    required_role = 'FINANCE'


class EmployeeOnly(RolePermission):
    required_role = 'EMPLOYEE'
