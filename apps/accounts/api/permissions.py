from typing import Type

from django.db.models import Model
from django.views.generic.base import View
from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from accounts.api.mixins import PermissionMixin


class RootPermission(PermissionMixin, BasePermission):
    pass


class IsSuperUser(RootPermission):
    def has_permission(self, request: Request, view: View) -> bool:
        return self.is_superuser(request)

    def has_object_permission(self, request: Request, view: View, obj: Type[Model]) -> bool:
        return self.is_superuser(request)


class IsDoctor(RootPermission):
    def has_permission(self, request: Request, view: View) -> bool:
        is_auth = self.is_authenticated(request)
        is_doc = request.user.user_type.doctor
        return True if is_auth and is_doc else False


class IsPatient(RootPermission):
    def has_permission(self, request: Request, view: View) -> bool:
        is_auth = self.is_authenticated(request)
        is_patient = self.has_group(request, 'patient')
        return is_auth and is_patient


class IsOwner(RootPermission):
    def has_object_permission(self, request: Request, view: View, obj: Type[Model]) -> bool:
        return self.is_owner(request, obj)


class CareDoctorReadOnly(RootPermission):
    def has_object_permission(self, request: Request, view: View, obj: Type[Model]) -> bool:
        if self.is_safe_method(request) and self.has_group(request, 'doctor'):
            return bool(obj.doctor_id == request.user.id)


class PatientReadOnly(RootPermission):
    def has_permission(self, request: Request, view: View) -> bool:
        return self.is_safe_method(request) and self.has_group(request, 'patient')


class RelatedPatientReadOnly(RootPermission):
    def has_object_permission(self, request: Request, view: View, obj: Type[Model]) -> bool:
        if self.is_safe_method(request) and self.has_group(request, 'patient'):
            user_patient_id = request.user.id
            return bool(obj.patient_id == user_patient_id)
        return False


class WithRelated(RootPermission):
    def has_object_permission(self, request: Request, view: View, obj: Type[Model]) -> bool:
        return self.is_related(request, obj)
