import datetime
from typing import Dict, Any, Tuple, List

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
    status = models.CharField(max_length=10, choices=HealthStatus.choices, default=HealthStatus.UNKNOWN)
    checked = models.BooleanField(default=False)
    # patient_checked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True


class PrescriptionQuerySet(models.QuerySet):
    def filter_writer(self, writer_id: int) -> 'PrescriptionQuerySet':
        return self.filter(writer_id=writer_id)

    def filter_patient(self, patient_id: int) -> 'PrescriptionQuerySet':
        return self.filter(patient_id=patient_id)

    # def defer_option_fields(self) -> 'PrescriptionQuerySet':
    #     deferred_doctor_field_set = get_defer_fields_set('writer', *DEFER_DOCTOR_FIELDS)
    #     deferred_patient_field_set = get_defer_fields_set('patient', *DEFER_PATIENT_FIELDS)
    #     return self.defer(*deferred_doctor_field_set, *deferred_patient_field_set)

    def select_patient(self) -> 'PrescriptionQuerySet':
        return self.select_related('patient')

    def select_writer(self) -> 'PrescriptionQuerySet':
        return self.select_related('writer__user').select_related('writer__major')

    def select_all(self) -> 'PrescriptionQuerySet':
        return self.select_patient().select_writer()

    def prefetch_doctor_file(self) -> 'PrescriptionQuerySet':
        return self.prefetch_related('doctor_files')

    def prefetch_file_prescription(self) -> 'PrescriptionQuerySet':
        return self.prefetch_related('file_prescriptions')

    def prefetch_file_prescription_with_files(self) -> 'PrescriptionQuerySet':
        return self.prefetch_related(Prefetch('file_prescriptions',
                                              queryset=FilePrescription.objects.prefetch_related('patient_files')
                                              ))

    def prefetch_all(self) -> 'PrescriptionQuerySet':
        return self.prefetch_file_prescription_with_files()

    # todo: 하드 코딩 -> 소프트 코딩으로 변경할 것
    def only_list(self, *others: List[str]):
        fields = PrescriptionFields.list_field + list(others)
        return self.only(*fields)

    def only_detail(self, *others: List[str]):
        fields = PrescriptionFields.detail_field + list(others)
        return self.only(*fields)


class PrescriptionManager(models.Manager):
    def get_queryset(self) -> 'PrescriptionQuerySet':
        return PrescriptionQuerySet(self.model, using=self._db). \
            annotate(user=F('writer_id'),
                     writer_name=concatenate_name('writer'),
                     patient_name=concatenate_name('patient'))

    def get_raw_queryset(self):
        return PrescriptionQuerySet(self.model, using=self._db)

    def prefetch_file_prescription(self) -> 'PrescriptionQuerySet':
        return self.get_queryset().prefetch_file_prescription()

    def select_all(self) -> 'PrescriptionQuerySet':
        return self.get_queryset().select_all().order_by('-created_at').filter(deleted=False)

    def nested_all(self) -> 'PrescriptionQuerySet':
        return self.get_queryset().select_all().prefetch_file_prescription_with_files(). \
            filter(deleted=False)


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

    class Meta:
        ordering = ['-id']

    def get_writer_name(self) -> str:
        return self.writer.get_full_name()

    def __str__(self) -> str:
        return f'{self.patient.get_full_name()}-{str(self.created_at)}'


@receiver(post_save, sender=Prescription)
def create_file_prescription(sender, **kwargs: Dict[str, Any]):
    instance = kwargs['instance']
    start_date = instance.start_date
    end_date = instance.end_date

    if not start_date or not end_date:
        return None

    bulk_list = (
        FilePrescription(
            prescription_id=instance.id,
            day_number=day_number + 1,
            day=start_date + datetime.timedelta(days=day_number))
        for day_number in range((end_date - start_date).days))
    FilePrescription.objects.bulk_create(bulk_list)


class FilePrescriptionQuerySet(models.QuerySet):
    # def defer_option_fields(self) -> 'FilePrescriptionQuerySet':
    #     deferred_doctor_field_set = get_defer_fields_set('writer', *DEFER_DOCTOR_FIELDS)
    #     deferred_patient_field_set = get_defer_fields_set('patient', *DEFER_PATIENT_FIELDS)
    #     return self.defer(*deferred_doctor_field_set, *deferred_patient_field_set)

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
        return self.filter(day__lt=datetime.date.today()).filter_not_checked().filter_not_uploaded()

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

    # todo: 하드 코딩 -> 소프트 코딩으로 변경할 것
    def only_list(self, *others: List[str]):
        fields = FilePrescriptionFields.list_field + list(others)
        return self.only(*fields)

    def only_detail(self, *others: List[str]):
        fields = FilePrescriptionFields.detail_field + list(others)
        return self.only(*fields)


class FilePrescriptionManager(models.Manager):
    def get_queryset(self) -> 'FilePrescriptionQuerySet':
        return FilePrescriptionQuerySet(self.model, using=self._db). \
            annotate(user=F('prescription__writer_id'),
                     doctor_id=F('prescription__writer_id'),  # 중복
                     patient_id=F('prescription__patient_id'),
                     writer_name=concatenate_name('prescription__writer'),
                     patient_name=concatenate_name('prescription__patient'))

    def prefetch_all(self) -> 'FilePrescriptionQuerySet':
        return self.get_queryset().prefetch_all()

    def select_all(self) -> 'FilePrescriptionQuerySet':
        return self.get_queryset().select_all()  # prescription-doctorfile, prescription-writer, patient_file

    def nested_all(self) -> 'FilePrescriptionQuerySet':
        return self.get_queryset().nested_all()


"""
FilePrescription
- fields: id, description, status, created_at, updated_at, deleted, prescription, day_number, active, checked 
"""


class FilePrescription(BasePrescription):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='file_prescriptions')
    day_number = models.IntegerField()
    day = models.DateField(null=True)
    active = models.BooleanField(default=True)
    uploaded = models.BooleanField(default=False)

    objects = FilePrescriptionManager()

    class Meta:
        ordering = ['-id']

    def __str__(self) -> str:
        return f'prescription_id:{self.prescription.id}-{self.day}: {self.day_number}일'


@receiver(post_save, sender=FilePrescription)
def set_prescription_checked(sender, **kwargs: Dict[str, Any]):
    instance = kwargs['instance']
    checked_queryset = instance.prescription.file_prescriptions.values_list('checked')

    if not checked_queryset.filter(checked=False).exists():
        instance.prescription.checked = True
        instance.prescription.save()
