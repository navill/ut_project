from typing import Type, Union, TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.db.models import QuerySet

from files.api.utils import delete_file

if TYPE_CHECKING:
    from files.models import DoctorFileQuerySet, PatientFileQuerySet

User = get_user_model()


class CommonUploaderCheckMixin:
    def filter_with_uploader(self, user: 'User', queryset: Type[QuerySet]) -> Type[QuerySet]:
        if user.user_type.doctor:
            queryset = queryset.select_doctor().select_prescription(). \
                filter_uploader(user)
        elif user.user_type.patient:
            queryset = queryset.select_patient().select_file_prescription().filter_uploader(user)
        return queryset if user.is_superuser else queryset


class CommonFileQuerysetMixin:
    def shallow_delete(self: Type['FileQuerySetMixin']) -> str:
        obj_name_list = [str(obj_name) for obj_name in self]
        self.update(deleted=True)
        return f'finish shallow delete [{obj_name_list}]'

    def hard_delete(self: Type['FileQuerySetMixin']) -> str:
        obj_name_list = []
        for doctor_file in self:
            obj_name_list.append(str(self))
            delete_file(doctor_file.file.path)
        super().delete()
        return f'finish hard delete [{obj_name_list}]'

    def filter_normal_list(self: Union['DoctorFileQuerySet', 'PatientFileQuerySet']) -> Type[QuerySet]:
        return self.filter(status='NORMAL')
