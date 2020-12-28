import datetime
import uuid

from django.contrib.auth import get_user_model
from django.db import models

from accounts.models import Patient, Doctor

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


def user_directory_path(instance: 'DataFile', filename: str) -> str:
    day, time = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S').split('_')
    name, ext = filename.split('.')
    # + MEDIA_ROOT
    return f'{instance.user.username}-{instance.user.id}/{instance.related_user}/{day}/{name}_{time}.{ext}'


class DataFileQueryManager(models.QuerySet):
    pass


class DataFileManager(models.Manager):
    def get_queryset(self):
        return DataFileQueryManager(self.model, using=self._db)

    def owner(self, user):
        queryset = self.get_queryset()
        if user.is_superuser:
            return queryset
        return queryset.filter(uploader=user.id)


class DataFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uploader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='files')
    # patient_name = models.CharField(max_length=255)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='files_by_doctor')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='files_by_patient')
    file = models.FileField(upload_to=user_directory_path)
    # file_name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    # updated_at = models.DateTimeField(auto_now=True)

    objects = DataFileManager()

    def __str__(self):
        return str(self.file)

    def is_uploader(self, user):
        if self.user.username == str(user.username):
            return True
        return False
