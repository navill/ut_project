import uuid
from typing import Dict, Any

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver

from files.api.mixins import CommonFileQuerysetMixin
from files.api.utils import delete_file, concatenate_name, directory_path
from prescriptions.models import Prescription, FilePrescription

User = get_user_model()


class BaseFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uploader = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
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
        return f'shallow delete [{obj_name}]'

    def hard_delete(self) -> str:
        obj_name = str(self)
        if self.file:
            delete_file(self.file.path)
        super().delete()
        return f'hard delete [{obj_name}]'


class DoctorFileQuerySet(CommonFileQuerysetMixin, models.QuerySet):
    def filter_not_deleted(self):
        return self.filter(deleted=False)

    def select_doctor(self) -> 'DoctorFileQuerySet':
        return self.annotate(uploader_doctor_name=concatenate_name('uploader__doctor'))

    def select_prescription(self) -> 'DoctorFileQuerySet':
        return self.annotate(patient_id=F('prescription__patient_id'))

    def select_all(self) -> 'DoctorFileQuerySet':
        return self.select_doctor().select_prescription()

    def filter_prescription_writer(self, current_user: User) -> 'DoctorFileQuerySet':
        # 접속자가 환자일 경우 환자(current_user.id)가 올린 파일 제외
        return self.filter(prescription__writer_id=current_user.id)

    def is_patient(self, doctor_id: int) -> 'DoctorFileQuerySet':
        return self.filter(uploader__patient__doctor_id=doctor_id)


class ParentDoctorFileManager(models.Manager):
    def select_all(self) -> DoctorFileQuerySet:
        return self.get_queryset().select_all()

    def filter_not_deleted(self):
        return self.get_queryset().filter_not_deleted()


class OriginDoctorFileManager(ParentDoctorFileManager):
    def get_queryset(self) -> DoctorFileQuerySet:
        return DoctorFileQuerySet(self.model, using=self._db). \
            annotate(user=F('uploader_id'))


class DoctorFileManager(ParentDoctorFileManager):
    def get_queryset(self) -> DoctorFileQuerySet:
        return DoctorFileQuerySet(self.model, using=self._db). \
            annotate(user=F('uploader_id')).order_by('-created_at')


class DoctorFile(BaseFile):
    prescription = models.ForeignKey(Prescription, on_delete=models.DO_NOTHING, null=True, related_name='doctor_files')

    objects = DoctorFileManager()
    origin_objects = OriginDoctorFileManager()


class PatientFileQuerySet(CommonFileQuerysetMixin, models.QuerySet):
    def filter_unchecked_list(self) -> 'PatientFileQuerySet':
        return self.filter(checked=False)

    def filter_checked_list(self) -> 'PatientFileQuerySet':
        return self.filter(checked=True)

    def filter_uploader(self, user_id) -> 'PatientFileQuerySet':
        return self.filter(uploader_id=user_id)

    def filter_not_deleted(self):
        return self.filter(deleted=False)

    def select_patient(self) -> 'PatientFileQuerySet':
        return self.annotate(uploader_patient_name=concatenate_name('uploader__patient'))

    def select_doctor(self) -> 'PatientFileQuerySet':
        return self.annotate(doctor_id=F('uploader__patient__doctor_id'))

    def select_file_prescription(self) -> 'PatientFileQuerySet':
        return self.select_related('file_prescription')

    def select_all(self) -> 'PatientFileQuerySet':
        return self.select_doctor().select_patient().select_file_prescription()


class ParentPatientFileManager(models.Manager):
    def select_all(self) -> PatientFileQuerySet:
        return self.get_queryset().select_all()


class OriginalPatientFileManager(ParentPatientFileManager):
    def get_queryset(self) -> PatientFileQuerySet:
        return PatientFileQuerySet(self.model, using=self._db). \
            annotate(user=F('uploader_id'))


class PatientFileManager(ParentPatientFileManager):
    def get_queryset(self) -> PatientFileQuerySet:
        return PatientFileQuerySet(self.model, using=self._db). \
            annotate(user=F('uploader_id')).order_by('-created_at')


class PatientFile(BaseFile):
    file_prescription = models.ForeignKey(FilePrescription, on_delete=models.DO_NOTHING, null=True,
                                          related_name='patient_files')

    objects = PatientFileManager()
    original_objects = OriginalPatientFileManager()


@receiver(post_save, sender=PatientFile)
def post_save_patient_file(sender, **kwargs: Dict[str, Any]):
    instance = kwargs['instance']
    file_prescription = instance.file_prescription
    if not file_prescription.uploaded:
        file_prescription.uploaded = True
        file_prescription.checked = False  # 환자가 파일을 업로드한 시점은 의사가 확인을 하지 않은 상태
        file_prescription.save()
