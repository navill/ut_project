from typing import Type, Union, TYPE_CHECKING

from django.db.models import QuerySet

if TYPE_CHECKING:
    from files.models import DoctorFileQuerySet, PatientFileQuerySet


class QuerySetMixin:
    def get_queryset(self) -> Type[QuerySet]:
        user = self.request.user
        queryset = super().get_queryset()
        if user.is_doctor:
            queryset = queryset.select_doctor().select_prescription(). \
                filter_prescription_writer(user)
        elif user.is_patient:
            queryset = queryset.select_patient().select_file_prescription().filter_uploader(user)
        return queryset if user.is_superuser else queryset

    # def _get_user_role(self, user):
    #     if user.is_doctor:
    #         query = 'uploader__doctor'
    #     elif user.is_patient:
    #         query = 'uploader__patient'
    #     return query


class BaseFileQuerySetMixin:
    def shallow_delete(self: Union['DoctorFileQuerySet', 'PatientFileQuerySet']) -> str:
        obj_name_list = [str(obj_name) for obj_name in self]
        self.update(deleted=True)
        return f'finish shallow delete [{obj_name_list}]'

    def hard_delete(self: Union['DoctorFileQuerySet', 'PatientFileQuerySet']) -> str:
        obj_name_list = []
        for file in self:
            obj_name_list.append(str(self))
            file.delete_file()
        super().delete()
        return f'finish hard delete [{obj_name_list}]'

    def filter_normal_list(self: Union['DoctorFileQuerySet', 'PatientFileQuerySet']) -> Type[QuerySet]:
        return self.filter(status='NORMAL')
