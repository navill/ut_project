import datetime
import uuid

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()
"""
hospital/
    department/
        doctor_name/ 
            patient_name/
                datetime/
                    files.txt
            patient_name/
                datetime/
                    files.mp4
                    images.img
"""


def directory_path(instance: 'DataFile', filename: str) -> str:
    day, time = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S').split('_')
    name, ext = filename.split('.')
    return f'{day}/{ext}/{instance.uploader}_{instance.patient}_{name}_{time}.{ext}'


class DataFileQuerySet(models.QuerySet):
    def owner_queryset(self, user):
        if user.is_superuser:
            return self
        return self.filter(uploader=user.id)


class DataFileManager(models.Manager):
    def get_queryset(self):
        return DataFileQuerySet(self.model, using=self._db).select_related('patient').select_related(
            'doctor').prefetch_related('uploader')


class DataFile(models.Model):
    """
    의사는 환자를 거쳐서만 데이터에 접근할 예정이므로 doctor와 관계를 맺을 필요없음
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uploader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='files', null=True)
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='files_by_patient', null=True)
    file = models.FileField(upload_to=directory_path)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    objects = DataFileManager()

    def __str__(self):
        return str(self.file)

    def is_uploader(self, user):
        if self.uploader.email == str(user.email):
            return True
        return False
