from rest_framework.permissions import BasePermission, SAFE_METHODS

from accounts.api.utils import is_authenticated, has_group, is_superuser, is_owner, is_safe_method, check_view


class RootPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return False

    def has_permission(self, request, view):
        return False


class IsSuperUser(RootPermission):
    def has_permission(self, request, view):
        return is_superuser(request)

    def has_object_permission(self, request, view, obj):
        return is_superuser(request)


class IsDoctor(RootPermission):
    def has_permission(self, request, view):
        is_auth = is_authenticated(request)
        is_doc = has_group(request, 'doctor')
        return is_auth and is_doc


class IsPatient(RootPermission):
    def has_permission(self, request, view):
        is_auth = is_authenticated(request)
        is_patient = has_group(request, 'patient')
        return is_auth and is_patient


class IsOwner(RootPermission):
    def has_permission(self, request, view):
        return check_view(view, 'Retrieve')

    def has_object_permission(self, request, view, obj):
        return is_owner(request, obj)


class CareDoctorReadOnly(RootPermission):
    def has_permission(self, request, view):
        return check_view(view, 'Retrieve')

    def has_object_permission(self, request, view, obj):
        return self._check_method_and_group(request) and bool(obj.user_doctor == request.user.doctor)

    def _check_method_and_group(self, request):
        return is_safe_method(request) and has_group(request, 'doctor')


class PatientReadOnly(RootPermission):
    def has_permission(self, request, view):
        return is_safe_method(request) and has_group(request, 'patient')


class RelatedPatientReadOnly(RootPermission):
    def has_object_permission(self, request, view, obj):
        if is_safe_method(request) and has_group(request, 'patient'):
            user_patient = request.user.patient
            return bool(obj.user_patient == user_patient)
        return False
