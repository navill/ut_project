import datetime

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


def user_directory_path(instance: 'DataFile', filename: str) -> str:
    day, time = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S').split('_')
    name, ext = filename.split('.')
    # instance.file_name = filename  # pre_save?
    return f'{day}/{instance.user}/{instance.related_user}/{name}_{time}.{ext}'


class DataFileQueryManager(models.QuerySet):
    def owner(self, user):
        if user.is_admin:
            return self
        return self.filter(user.id)


class DataFileManager(models.Manager):
    def get_queryset(self):
        return DataFileQueryManager(self.model, using=self._db)

    def owner(self, user):
        return self.get_queryset().owner(user)


class DataFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='files')
    related_user = models.CharField(max_length=255)
    file = models.FileField(upload_to=user_directory_path)
    file_name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = DataFileManager()

    def __str__(self):
        return str(self.file_name)

    def is_owner(self, user):
        if self.user.username == str(user):
            return True
        return False

# pre_save() => file_name(?)