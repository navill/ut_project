from rest_framework.permissions import BasePermission

from accounts.api.utils import is_authenticated, has_group, is_superuser, is_owner, is_safe_method


class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return is_superuser(request)

    def has_object_permission(self, request, view, obj):
        return is_superuser(request)


class IsDoctor(BasePermission):
    def has_permission(self, request, view):
        is_auth = is_authenticated(request)
        is_doc = has_group(request, 'doctor')
        return is_auth and is_doc


class IsPatient(BasePermission):
    def has_permission(self, request, view):
        is_auth = is_authenticated(request)
        is_patient = has_group(request, 'patient')
        return is_auth and is_patient


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return is_owner(request, obj)


class CareDoctorReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):  # retrieve, update
        if is_safe_method(request) and has_group(request, 'doctor'):
            return bool(obj.doctor == request.user.doctor)


class PatientReadOnly(BasePermission):
    def has_permission(self, request, view):
        return is_safe_method(request) and has_group(request, 'patient')


class RelatedPatientReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if is_safe_method(request) and has_group(request, 'patient'):
            user_patient = request.user.patient
            return bool(obj.user_patient == user_patient)
        return False
