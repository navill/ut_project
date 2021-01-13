import datetime
import uuid
from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F
from django.db.models.functions import Concat

from files.api.utils import delete_file
from prescriptions.models import Prescription

if TYPE_CHECKING:
    from accounts.models import BaseUser

User = get_user_model()


def concatenate_name(target_field: str):
    full_name = Concat(F(f'{target_field}__first_name'), F(f'{target_field}__last_name'))
    return full_name


DEFAULT_QUERY_FIELDS = ('id', 'prescription', 'uploader_id', 'file', 'created_at', 'checked')
UPLOADER_QUERY_FIELDS = ('user_id', 'first_name', 'last_name')
PRESCRIPTION_QUERY_FIELD = ('prescription__id',)

DOCTOR_QUERY_FIELDS = (f'uploader__doctor__{field}' for field in UPLOADER_QUERY_FIELDS)
PATIENT_QUERY_FIELDS = (f'uploader__patient__{field}' for field in UPLOADER_QUERY_FIELDS)


def directory_path(instance: 'DataFile', filename: str) -> str:
    day, time = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S').split('_')
    name, ext = filename.split('.')
    return f'{day}/{ext}/{instance.uploader}_{name}_{time}.{ext}'


"""
[uploader]
- uploader는 patient 또는 doctor 객체가 올 수 있다.
doctor: 의사가 업로드한 파일 리스트만 출력해야한다.
patient: 환자가 업로드한 파일 리스트만 출력해야한다.
공통사항: filter(prescription__writer=current_user_id) + filter(uploader_id=current_user_id)

Superuser는 모든 파일 리스트를 출력할 수 있다.
"""


class DataFileQuerySet(models.QuerySet):
    def shallow_delete(self):
        self.update(deleted=True)

    def hard_delete(self):
        for file in self:
            file.delete_file()
        super().delete()

    def necessary_fields(self, *fields):
        return self.only(*DEFAULT_QUERY_FIELDS, *DOCTOR_QUERY_FIELDS, *PATIENT_QUERY_FIELDS, *fields)

    def unchecked_list(self):
        return self.filter(checked=False)

    def normal_status_list(self):
        return self.filter(status='NORMAL')

    def filter_uploader(self, current_user: 'BaseUser'):
        return self.filter(user=current_user.id)

    def filter_prescription_writer(self, current_user: 'BaseUser'):
        # 접속자가 환자일 경우 환자(current_user.id)가 올린 파일 제외
        return self.filter(prescription__writer=current_user.id)

    def filter_prescription_related_patient(self, current_user: 'BaseUser'):
        return self.filter(prescription__patient=current_user.id)

    def join_uploader(self, role: str):
        return self.select_related(role)

    def join_prescription_writer(self):
        return self.select_related('prescription__writer')

    def select_all(self):
        return self.select_related('prescription__writer').select_related('uploader')


class DataFileManager(models.Manager):
    def get_queryset(self):
        return DataFileQuerySet(self.model, using=self._db). \
            annotate(user=F('uploader_id')).order_by('-created_at')

    def owner_queryset(self, user):
        if user.is_superuser:
            return self
        return self.get_queryset().filter(user=user.id)


class HealthStatus(models.TextChoices):
    NORMAL = 'NORMAL', '정상'
    ABNORMAL = 'ABNORMAL', '비정상'
    UNKNOWN = 'UNKNOWN', '알 수 없음'


class DataFile(models.Model):
    # necessary fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prescription = models.ForeignKey(Prescription, on_delete=models.DO_NOTHING, null=True)
    uploader = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='files', null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    file = models.FileField(upload_to=directory_path, null=True)

    # option fields
    checked = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=HealthStatus.choices, default=HealthStatus.UNKNOWN)
    deleted = models.BooleanField(default=False)

    objects = DataFileManager()

    def __str__(self):
        return str(self.file)

    def is_uploader(self, user):
        if self.uploader.email == str(user.email):
            return True
        return False

    def shallow_delete(self):
        self.deleted = True
        self.save()

    def hard_delete(self):
        if self.file:
            delete_file(self.file.path)
        super().delete()
