from __future__ import annotations

import uuid
from typing import Type, Dict, Any, Union

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F, QuerySet
from django.db.models.signals import post_save
from django.dispatch import receiver

from files.api.utils import delete_file, concatenate_name, directory_path
from prescriptions.models import Prescription, FilePrescription

User = get_user_model()

BASE_QUERY_FIELDS = ('id', 'uploader_id', 'file', 'created_at', 'checked', 'deleted')
UPLOADER_QUERY_FIELDS = ('user_id', 'first_name', 'last_name')
PRESCRIPTION_QUERY_FIELD = ('prescription__id',)

DOCTOR_QUERY_FIELDS = (f'uploader__doctor__{field}' for field in UPLOADER_QUERY_FIELDS)
PATIENT_QUERY_FIELDS = (f'uploader__patient__{field}' for field in UPLOADER_QUERY_FIELDS)


class BaseFileQuerySetMixin:
    def shallow_delete(self: Union[DoctorFileQuerySet, PatientFileQuerySet]) -> str:
        obj_name_list = [str(obj_name) for obj_name in self]
        self.update(deleted=True)
        return f'finish shallow delete [{obj_name_list}]'

    def hard_delete(self: Union[DoctorFileQuerySet, PatientFileQuerySet]) -> str:
        obj_name_list = []
        for file in self:
            obj_name_list.append(str(self))
            file.delete_file()
        super().delete()
        return f'finish hard delete [{obj_name_list}]'

    def filter_normal_list(self: Union[DoctorFileQuerySet, PatientFileQuerySet]) -> Type[QuerySet]:
        return self.filter(status='NORMAL')


class BaseFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uploader = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    file = models.FileField(upload_to=directory_path, null=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return str(self.file)

    def is_uploader(self, user: User) -> bool:
        if self.uploader.email == str(user.email):
            return True
        return False

    def shallow_delete(self) -> str:
        obj_name = str(self)
        self.deleted = True
        self.save()
        return f'finish shallow delete [{obj_name}]'

    def hard_delete(self) -> str:
        obj_name = str(self)
        if self.file:
            delete_file(self.file.path)
        super().delete()
        return f'finish hard delete [{obj_name}]'


class DoctorFileQuerySet(BaseFileQuerySetMixin, models.QuerySet):
    def select_doctor(self) -> 'DoctorFileQuerySet':
        return self.select_related('uploader__doctor')

    def select_prescription(self) -> 'DoctorFileQuerySet':
        return self.select_related('prescription')

    def select_all(self) -> 'DoctorFileQuerySet':
        return self.select_doctor().select_prescription()

    def filter_prescription_writer(self, current_user: User) -> 'DoctorFileQuerySet':
        # 접속자가 환자일 경우 환자(current_user.id)가 올린 파일 제외
        return self.filter(prescription__writer_id=current_user.id)


class DoctorFileManager(models.Manager):
    def get_queryset(self) -> DoctorFileQuerySet:
        return DoctorFileQuerySet(self.model, using=self._db). \
            annotate(user=F('uploader_id'),
                     uploader_doctor_name=concatenate_name('uploader__doctor')). \
            order_by('-created_at')

    def select_all(self) -> DoctorFileQuerySet:
        return self.get_queryset().select_all()


class DoctorFile(BaseFile):
    prescription = models.ForeignKey(Prescription, on_delete=models.DO_NOTHING)

    objects = DoctorFileManager()


class PatientFileQuerySet(BaseFileQuerySetMixin, models.QuerySet):
    def filter_unchecked_list(self) -> 'PatientFileQuerySet':
        return self.filter(checked=False)

    def filter_checked_list(self) -> 'PatientFileQuerySet':
        return self.filter(checked=True)

    def filter_uploader(self, user) -> 'PatientFileQuerySet':
        return self.filter(uploader=user)

    def select_patient(self) -> 'PatientFileQuerySet':
        return self.select_related('uploader__patient')

    def select_doctor(self) -> 'PatientFileQuerySet':
        return self.select_related('prescription__doctor')

    def select_file_prescription(self) -> 'PatientFileQuerySet':
        return self.select_related('file_prescription')

    def select_all(self) -> 'PatientFileQuerySet':
        return self.select_patient().select_file_prescription()


class PatientFileManager(models.Manager):
    def get_queryset(self) -> PatientFileQuerySet:
        return PatientFileQuerySet(self.model, using=self._db). \
            annotate(user=F('uploader_id'),
                     uploader_patient_name=concatenate_name('uploader__patient')). \
            order_by('-created_at')

    def select_all(self) -> PatientFileQuerySet:
        return self.get_queryset().select_all()


class PatientFile(BaseFile):
    file_prescription = models.ForeignKey(FilePrescription, on_delete=models.DO_NOTHING, related_name='patient_files')

    objects = PatientFileManager()


@receiver(post_save, sender=PatientFile)
def create_patient_file(sender, **kwargs: Dict[str, Any]):
    instance = kwargs['instance']
    file_prescription = instance.file_prescription
    if not file_prescription.uploaded:
        file_prescription.uploaded = True
        file_prescription.save()
