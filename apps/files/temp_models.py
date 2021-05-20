import datetime

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from accounts.models import Doctor

FILE_TYPE = {
    'ECG': 'C',
    'EMG': 'M',
    'VOICE': 'V',
    'FACE': 'F',
}


# _temp_directory_path, FileHandler: refactoring은 나중에...

def _temp_directory_path(instance, filename):
    day, time = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S').split('_')
    splited_name = filename.split('.')

    splited_filename = splited_name[:-1][0]
    extension = splited_name[-1]
    for key, value in FILE_TYPE.items():
        if splited_filename.startswith(key):
            splited_filename = splited_filename.replace(key, value)

    return f'Chosun/{day}/{extension}/{splited_filename}_{instance.doctor.user.email}_{time}.{extension}'


class TempHospitalFiles(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=255, null=True)
    file_info = models.TextField(null=True)
    file_type = models.CharField(max_length=255, null=True)
    file = models.FileField(upload_to=_temp_directory_path)
    extension = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


@receiver(pre_save, sender=TempHospitalFiles)
def pre_save_temp_files(sender, **kwargs):
    instance = kwargs['instance']
    handler = FileHandler(instance)
    handler.set_attributes()
    instance.file_name = handler.file_name
    instance.file_type = handler.file_type
    instance.extension = handler.extension


# ECG_sdflasjdkra.png -> C_20210501_00:00:00.png

class FileHandler:
    def __init__(self, instance):
        self.file = instance.file
        self.file_type = None
        self.extension = None
        self.file_name = None
        self.container = {}

    def divide_file_string(self):
        full_name, extension = str(self.file.name).split('.')
        name_list = str(full_name).split('_')

        if len(name_list) == 1:
            raise Exception('invalid file type')

        file_type, name = name_list[0], name_list[1:]
        if file_type in FILE_TYPE.keys():
            file_type = FILE_TYPE[file_type]
        file_name = '_'.join(name)
        self.build_container(extension=extension, file_type=file_type, file_name=file_name)

    def build_container(self, **kwargs):
        self.container.update(**kwargs)

    def set_attributes(self):
        self.divide_file_string()
        [setattr(self, key, value) for key, value in self.container.items()]
