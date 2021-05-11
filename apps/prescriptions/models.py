import datetime
from typing import Dict, Any, List, NoReturn

from django.db import models
from django.db.models import F, Prefetch
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import Patient, Doctor
from core.api.fields import FilePrescriptionFields, PrescriptionFields
from prescriptions.api.utils import concatenate_name


class HealthStatus(models.TextChoices):
    NONE = 'NONE', '없음'
    NORMAL = 'NORMAL', '정상'
    ABNORMAL = 'ABNORMAL', '비정상'
    UNKNOWN = 'UNKNOWN', '알 수 없음'


class BasePrescription(models.Model):
    description = models.TextField()
    description_for_patient = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=HealthStatus.choices, default=HealthStatus.UNKNOWN)
    checked = models.BooleanField(default=False)
    checked_by_patient = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True


class PrescriptionQuerySet(models.QuerySet):
    def select_patient(self) -> 'PrescriptionQuerySet':
        return self.select_related('patient')

    def select_writer(self) -> 'PrescriptionQuerySet':
        return self.select_related('writer').select_related('writer__major')

    def select_all(self) -> 'PrescriptionQuerySet':
        return self.select_patient().select_writer()

    def prefetch_doctor_file(self) -> 'PrescriptionQuerySet':
        return self.prefetch_related('doctor_files')

    def prefetch_file_prescription(self) -> 'PrescriptionQuerySet':
        return self.prefetch_related('file_prescriptions')

    def prefetch_file_prescription_with_files(self) -> 'PrescriptionQuerySet':
        return self.prefetch_related(Prefetch('file_prescriptions',
                                              queryset=FilePrescription.objects.prefetch_related('patient_files')))

    def prefetch_all(self) -> 'PrescriptionQuerySet':
        return self.prefetch_file_prescription_with_files()

    def only_list(self, *others: List[str]):
        fields = PrescriptionFields.list_field + list(others)
        return self.only(*fields)

    def only_detail(self, *others: List[str]):
        fields = PrescriptionFields.detail_field + list(others)
        return self.only(*fields)

    def choice_fields(self):
        return self.only('id', 'writer_id', 'patient_id', 'start_date', 'end_date',
                         'created_at', 'status', 'checked')


class ParentPrescriptionManager(models.Manager):
    def select_all(self) -> 'PrescriptionQuerySet':
        return self.get_queryset().select_all().order_by('-created_at').filter(deleted=False)

    def nested_all(self) -> 'PrescriptionQuerySet':
        return self.get_queryset().select_all().prefetch_file_prescription_with_files(). \
            filter(deleted=False)

    def choice_fields(self):
        return self.get_queryset().choice_fields()


class OriginPrescriptionManager(ParentPrescriptionManager):
    def get_queryset(self) -> 'PrescriptionQuerySet':
        return PrescriptionQuerySet(self.model, using=self._db). \
            annotate(user=F('writer_id'))


class PrescriptionManager(ParentPrescriptionManager):
    def get_queryset(self) -> 'PrescriptionQuerySet':
        return PrescriptionQuerySet(self.model, using=self._db). \
            annotate(user=F('writer_id'),
                     writer_name=concatenate_name('writer'),
                     patient_name=concatenate_name('patient'))


"""
Prescription
- fields: id, description, status, created_at, updated_at, deleted, writer, patient, start_date, end_date 
"""


class Prescription(BasePrescription):
    writer = models.ForeignKey(Doctor, on_delete=models.DO_NOTHING, related_name='prescriptions')
    patient = models.ForeignKey(Patient, on_delete=models.DO_NOTHING, related_name='prescriptions')
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)

    objects = PrescriptionManager()
    origin_objects = OriginPrescriptionManager()

    class Meta:
        ordering = ['-created_at']

    def get_writer_name(self) -> str:
        return self.writer.get_full_name()

    def __str__(self) -> str:
        return f'{self.patient.get_full_name()}-{str(self.created_at)}'


class FilePrescriptionQuerySet(models.QuerySet):
    def filter_uploaded(self) -> 'FilePrescriptionQuerySet':
        return self.filter(uploaded=True)

    def filter_not_uploaded(self) -> 'FilePrescriptionQuerySet':
        return self.filter(uploaded=False)

    def filter_checked(self) -> 'FilePrescriptionQuerySet':
        return self.filter(checked=True)

    def filter_not_checked(self) -> 'FilePrescriptionQuerySet':
        return self.filter(checked=False)

    def filter_new_uploaded_file(self) -> 'FilePrescriptionQuerySet':
        return self.filter_uploaded().filter_not_checked()

    def filter_upload_date_expired(self) -> 'FilePrescriptionQuerySet':
        return self.filter(date__lt=datetime.date.today()).filter_not_checked().filter_not_uploaded()

    def filter_prescription_writer(self, user_id: int) -> 'FilePrescriptionQuerySet':
        return self.filter(prescription__writer_id=user_id)

    def prefetch_doctor_files(self) -> 'FilePrescriptionQuerySet':
        return self.prefetch_related('prescription__doctor_files')

    def prefetch_patient_files(self) -> 'FilePrescriptionQuerySet':
        return self.prefetch_related('patient_files')

    def prefetch_all(self) -> 'FilePrescriptionQuerySet':
        return self.prefetch_patient_files().prefetch_doctor_files()

    def select_all(self) -> 'FilePrescriptionQuerySet':
        return self.select_related('prescription__writer')

    def nested_all(self) -> 'FilePrescriptionQuerySet':
        return self.select_all().prefetch_all()

    def only_list(self, *others: List[str]) -> 'FilePrescriptionQuerySet':
        fields = FilePrescriptionFields.list_field + list(others)
        return self.only(*fields)

    def only_detail(self, *others: List[str]) -> 'FilePrescriptionQuerySet':
        fields = FilePrescriptionFields.detail_field + list(others)
        return self.only(*fields)

    def choice_fields(self) -> 'FilePrescriptionQuerySet':
        return self.only('id', 'status', 'created_at', 'date', 'day_number', 'active', 'uploaded', 'checked')

    def annotate_user(self) -> 'FilePrescriptionQuerySet':
        return self.annotate(user=F('prescription__writer_id'))


class ParentFilePrescriptionManager(models.Manager):
    def prefetch_all(self) -> 'FilePrescriptionQuerySet':
        return self.get_queryset().prefetch_all()

    def select_all(self) -> 'FilePrescriptionQuerySet':
        return self.get_queryset().select_all()

    def nested_all(self) -> 'FilePrescriptionQuerySet':
        return self.get_queryset().nested_all()

    def choice_fields(self) -> 'FilePrescriptionQuerySet':
        return self.get_queryset().choice_fields()


class OriginalFilePrescriptionManager(ParentFilePrescriptionManager):
    def get_queryset(self) -> 'FilePrescriptionQuerySet':
        return FilePrescriptionQuerySet(self.model, using=self._db).annotate_user()


class FilePrescriptionManager(ParentFilePrescriptionManager):
    def get_queryset(self) -> 'FilePrescriptionQuerySet':
        return FilePrescriptionQuerySet(self.model, using=self._db). \
            filter(deleted=False).annotate_user().annotate(writer_id=F('prescription__writer_id'),
                                                           patient_id=F('prescription__patient_id'),
                                                           writer_name=concatenate_name('prescription__writer'),
                                                           patient_name=concatenate_name('prescription__patient'))

    def unchecked_by(self, prescription_id) -> FilePrescriptionQuerySet:
        return FilePrescriptionQuerySet(self.model, using=self._db).filter(prescription_id=prescription_id).filter(
            checked=False)


class FilePrescription(BasePrescription):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='file_prescriptions')
    day_number = models.IntegerField()
    date = models.DateField(null=True)
    active = models.BooleanField(default=True)
    uploaded = models.BooleanField(default=False)

    objects = FilePrescriptionManager()
    origin_objects = OriginalFilePrescriptionManager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'prescription_id:{self.prescription.id}-{self.date}: {self.day_number}일'


class ParentCheckHandler:
    def __init__(self, instance):
        self.prescription = instance.prescription
        self.file_prescription = instance

    def update_prescription(self):
        check_flag = self.convert_checked_flag()
        self.update_prescription_checked(check_flag)

    def convert_checked_flag(self) -> bool:
        check_flag = False

        if self.has_all_checked(self.file_prescription) and self.is_checked(self.prescription) is False:
            check_flag = True
        elif self.is_checked(self.prescription):
            check_flag = False
        return check_flag

    def update_prescription_checked(self, check_value: bool) -> NoReturn:
        self.prescription.checked = check_value
        self.prescription.save()

    def has_all_checked(self, file_prescription: FilePrescription) -> bool:
        file_prescriptions = FilePrescription.objects.unchecked_by(file_prescription.prescription_id)
        return not file_prescriptions.exists()

    def is_checked(self, prescription: Prescription) -> bool:
        return prescription.checked


# 단일 FilePrescription 업데이트 시
@receiver(post_save, sender=FilePrescription)
def post_save_file_prescription(sender, **kwargs: Dict[str, Any]):
    handler = ParentCheckHandler(kwargs['instance'])
    handler.update_prescription()


# TextField Lookup - Full-text search
@models.TextField.register_lookup
class FullTextSearch(models.Lookup):
    lookup_name = "search"

    def as_mysql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return f"MATCH (%s) AGAINST (%s IN BOOLEAN MODE)" % (lhs, rhs), params
