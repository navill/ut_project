import datetime
import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F

from prescriptions.models import Prescription

User = get_user_model()


def directory_path(instance: 'DataFile', filename: str) -> str:
    day, time = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S').split('_')
    name, ext = filename.split('.')
    return f'{day}/{ext}/{instance.uploader}_{name}_{time}.{ext}'


class DataFileQuerySet(models.QuerySet):
    def necessary_fields(self, *args: str):
        return self.only('id', 'uploader_id', 'prescription_id', 'created_at', *args)

    def unchecked_list(self):
        return self.filter(checked=False)

    def normal_status_list(self):
        return self.filter(status='NORMAL')

    def filter_current_user(self, uploader):
        return self.filter(uploader=uploader)

    def related_prescription(self):
        return self.select_related('prescription')


class DataFileManager(models.Manager):
    def get_queryset(self):
        return DataFileQuerySet(self.model, using=self._db).select_related('uploader__doctor').select_related(
            'uploader__patient').annotate(user=F('uploader_id')).order_by('-created_at')

    def owner_queryset(self, user):
        if user.is_superuser:
            return self
        return self.get_queryset().filter(uploader=user.id)


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

    # option fields
    file = models.FileField(upload_to=directory_path, null=True)
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
