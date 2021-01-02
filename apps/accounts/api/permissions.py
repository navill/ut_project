from rest_framework.permissions import BasePermission

from accounts.api.mixins import PermissionMethodBundleMixin


class RootPermission(PermissionMethodBundleMixin, BasePermission):
    pass


class IsSuperUser(RootPermission):
    def has_permission(self, request, view):
        return self.is_superuser(request)

    def has_object_permission(self, request, view, obj):
        return self.is_superuser(request)


class IsDoctor(RootPermission):
    def has_permission(self, request, view):
        is_auth = self.is_authenticated(request)
        is_doc = self.has_group(request, 'doctor')
        return is_auth and is_doc


class IsPatient(RootPermission):
    def has_permission(self, request, view):
        is_auth = self.is_authenticated(request)
        is_patient = self.has_group(request, 'patient')
        return is_auth and is_patient


class IsOwner(RootPermission):
    def has_object_permission(self, request, view, obj):
        return self.is_owner(request, obj)


class CareDoctorReadOnly(RootPermission):
    def has_object_permission(self, request, view, obj):
        if self.is_safe_method(request) and self.has_group(request, 'doctor'):
            return bool(obj.doctor == request.user.doctor)


class PatientReadOnly(RootPermission):
    def has_permission(self, request, view):
        return self.is_safe_method(request) and self.has_group(request, 'patient')


class RelatedPatientReadOnly(RootPermission):
    def has_object_permission(self, request, view, obj):
        if self.is_safe_method(request) and self.has_group(request, 'patient'):
            user_patient = request.user.patient
            return bool(obj.user_patient == user_patient)
        return False
