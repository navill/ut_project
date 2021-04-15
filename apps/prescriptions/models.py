import datetime
from typing import Dict, Any, List

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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True


class PrescriptionQuerySet(models.QuerySet):
    # [Deprecated]
    # def is_writer(self, writer_id: int) -> 'PrescriptionQuerySet':
    #     return self.filter(writer_id=writer_id)
    #
    # def is_patient(self, patient_id: int) -> 'PrescriptionQuerySet':
    #     return self.filter(patient_id=patient_id)

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


class PrescriptionManager(models.Manager):
    def get_queryset(self) -> 'PrescriptionQuerySet':
        return PrescriptionQuerySet(self.model, using=self._db). \
            annotate(user=F('writer_id'),
                     writer_name=concatenate_name('writer'),
                     patient_name=concatenate_name('patient'))

    # [Deprecated]
    # def prefetch_file_prescription(self) -> 'PrescriptionQuerySet':
    #     return self.get_queryset().prefetch_file_prescription()

    def select_all(self) -> 'PrescriptionQuerySet':
        return self.get_queryset().select_all().order_by('-created_at').filter(deleted=False)

    def nested_all(self) -> 'PrescriptionQuerySet':
        return self.get_queryset().select_all().prefetch_file_prescription_with_files(). \
            filter(deleted=False)

    def choice_fields(self):
        return self.get_queryset().choice_fields()


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
        ordering = ['-created_at']

    def get_writer_name(self) -> str:
        return self.writer.get_full_name()

    def __str__(self) -> str:
        return f'{self.patient.get_full_name()}-{str(self.created_at)}'


# [Deprecated]
# 문제: 업데이트할 때 마다 signal 호출
# => signal 대신 serializer에서 처리(PrescriptionSerializerMixin)
# @receiver(post_save, sender=Prescription)
# def create_file_prescription_by_prescription(sender, **kwargs: Dict[str, Any]):
#     instance = kwargs['instance']
#     start_date = instance.start_date
#     end_date = instance.end_date
#
#     if not start_date or not end_date:
#         return None
#
#     bulk_list = (
#         FilePrescription(
#             prescription_id=instance.id,
#             day_number=day_number + 1,
#             date=start_date + datetime.timedelta(days=day_number))
#         for day_number in range((end_date - start_date).days + 1))
#     FilePrescription.objects.bulk_create(bulk_list)


class FilePrescriptionQuerySet(models.QuerySet):
    def update(self, **kwargs):
        super().update(**kwargs)
        self.first().save()

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

    def only_list(self, *others: List[str]):
        fields = FilePrescriptionFields.list_field + list(others)
        return self.only(*fields)

    def only_detail(self, *others: List[str]) -> 'FilePrescriptionQuerySet':
        fields = FilePrescriptionFields.detail_field + list(others)
        return self.only(*fields)

    def choice_fields(self) -> 'FilePrescriptionQuerySet':
        return self.only('id', 'status', 'created_at', 'date', 'day_number', 'active', 'uploaded', 'checked')


class FilePrescriptionManager(models.Manager):
    def get_queryset(self) -> 'FilePrescriptionQuerySet':
        return FilePrescriptionQuerySet(self.model, using=self._db). \
            filter(deleted=False).annotate(user=F('prescription__writer_id'),
                                           writer_id=F('prescription__writer_id'),
                                           patient_id=F('prescription__patient_id'),
                                           writer_name=concatenate_name('prescription__writer'),
                                           patient_name=concatenate_name('prescription__patient'))

    def prefetch_all(self) -> 'FilePrescriptionQuerySet':
        return self.get_queryset().prefetch_all()

    def select_all(self) -> 'FilePrescriptionQuerySet':
        return self.get_queryset().select_all()

    def nested_all(self) -> 'FilePrescriptionQuerySet':
        return self.get_queryset().nested_all()

    def choice_fields(self) -> 'FilePrescriptionQuerySet':
        return self.get_queryset().choice_fields()


class FilePrescription(BasePrescription):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='file_prescriptions')
    day_number = models.IntegerField()
    date = models.DateField(null=True)
    active = models.BooleanField(default=True)
    uploaded = models.BooleanField(default=False)

    objects = FilePrescriptionManager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'prescription_id:{self.prescription.id}-{self.date}: {self.day_number}일'


@receiver(post_save, sender=FilePrescription)
def set_prescription_checked(sender, **kwargs: Dict[str, Any]):
    instance = kwargs['instance']
    not_checked_queryset = FilePrescription.objects.filter(prescription_id=instance.prescription_id).filter(
        checked=False)
    parent_prescription = instance.prescription
    check_value = False

    if not not_checked_queryset.exists() and parent_prescription.checked is False:
        check_value = True
    elif parent_prescription.checked:
        check_value = False

    parent_prescription.checked = check_value
    parent_prescription.save()


# TextField Lookup - Full-text search
@models.TextField.register_lookup
class FullTextSearch(models.Lookup):
    lookup_name = "search"

    def as_mysql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return f"MATCH (%s) AGAINST (%s IN BOOLEAN MODE)" % (lhs, rhs), params
