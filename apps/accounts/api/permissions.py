from rest_framework.permissions import BasePermission, IsAuthenticated


class AccountsPermissionMixin(BasePermission):
    def is_superuser(self, request):
        return bool(request.user and request.user.is_superuser)

    def check_owner(self, request, obj):
        user = request.user
        owner = None
        if hasattr(obj, 'user'):
            owner = obj.user
        elif hasattr(obj, 'writer'):
            owner = obj.writer
        return bool(user == owner)


class IsDoctor(IsAuthenticated):
    def has_permission(self, request, view):  # todo: rest freamework render에서 한번 더 호출되는 문제
        is_auth = super().has_permission(request, view)
        is_doc = request.user.groups.filter(name='doctor').exists()
        return bool(is_auth and is_doc)


class IsPatient(IsAuthenticated):
    def has_permission(self, request, view):  # todo: rest freamework render에서 한번 더 호출되는 문제
        is_auth = super().has_permission(request, view)
        is_patient = request.user.groups.filter(name='patient').exists()
        return bool(is_auth and is_patient)


class IsSuperUser(AccountsPermissionMixin):
    def has_permission(self, request, view):
        return self.is_superuser(request)

    def has_object_permission(self, request, view, obj):
        return self.is_superuser(request)


class OnlyOwner(AccountsPermissionMixin):
    def has_object_permission(self, request, view, obj):
        return self.check_owner(request, obj)


class OwnerUpdateOrReadDoctor(AccountsPermissionMixin):
    def has_object_permission(self, request, view, obj):
        is_owner = self.check_owner(request, obj)
        is_doc = request.user.groups.filter(name='doctor').exists()
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            return is_owner
        else:
            return is_owner or is_doc


class OnlyHasPatient(AccountsPermissionMixin):
    def has_object_permission(self, request, view, obj):
        user = request.user
        user_patient = None
        if hasattr(user, 'patient'):
            user_patient = request.user.patient
        return obj.user_patient == user_patient

# chain response pattern?
# OnlyOwner -> OnlyHasPatient -> IsSuperUser -> False
