import datetime
import uuid

from django.contrib.auth import get_user_model
from django.db import models

from prescriptions.models import Prescription

User = get_user_model()


def directory_path(instance: 'DataFile', filename: str) -> str:
    day, time = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S').split('_')
    name, ext = filename.split('.')
    return f'{day}/{ext}/{instance.uploader}_{name}_{time}.{ext}'


class DataFileQuerySet(models.QuerySet):
    def get_unchecked_list(self):
        return self.filter(checked=False)

    def get_normal_status_list(self):
        return self.filter(status='NORMAL')

    def filter_current_user(self, uploader):
        return self.filter(uploader=uploader)

    def related_uploader(self, uploader):
        queryset = None
        if uploader.is_doctor:
            queryset = self.select_related('uploader__doctor').order_by('-created_at')
        elif uploader.is_patient:
            queryset = self.select_related('uploader__patient').order_by('-created_at')
        return queryset

    # def get_queryset_related_doctor(self):


class DataFileManager(models.Manager):
    def get_queryset(self):
        return DataFileQuerySet(self.model, using=self._db)

    def owner_queryset(self, user):
        if user.is_superuser:
            return self
        return self.get_queryset().filter(uploader=user.id)


class HealthStatus(models.TextChoices):
    NORMAL = 'NORMAL', '정상'
    ABNORMAL = 'ABNORMAL', '비정상'
    UNKNOWN = 'UNKNOWN', '알 수 없음'


class DataFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prescription = models.ForeignKey(Prescription, on_delete=models.SET_NULL, null=True)
    uploader = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='files', null=True)
    file = models.FileField(upload_to=directory_path)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    checked = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=HealthStatus.choices, default=HealthStatus.UNKNOWN)

    objects = DataFileManager()

    def __str__(self):
        return str(self.file)

    def is_uploader(self, user):
        if self.uploader.email == str(user.email):
            return True
        return False

    # file에 접근할 수 있는 유저: uploader or prescription.writer
