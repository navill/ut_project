from django.db import models
from django.db.models import F, Prefetch
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import Patient, Doctor, DEFER_PATIENT_FIELDS, DEFER_DOCTOR_FIELDS
from files.api.utils import directory_path
from prescriptions.api.utils import get_defer_fields_set, concatenate_name


class HealthStatus(models.TextChoices):
    NONE = 'NONE', '없음'
    NORMAL = 'NORMAL', '정상'
    ABNORMAL = 'ABNORMAL', '비정상'
    UNKNOWN = 'UNKNOWN', '알 수 없음'


class BasePrescription(models.Model):
    description = models.TextField()
    status = models.CharField(max_length=10, choices=HealthStatus.choices, default=HealthStatus.UNKNOWN)
    checked = models.BooleanField(default=False)  # 환자가 파일 업로드할 때 True, 의사가 FilePrescription 생성할 때 False

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

    def join_uploader(self, query_word: str) -> 'PrescriptionQuerySet':
        return self.select_related(query_word)

    def defer_option_fields(self) -> 'PrescriptionQuerySet':
        deferred_doctor_field_set = get_defer_fields_set('writer', *DEFER_DOCTOR_FIELDS)
        deferred_patient_field_set = get_defer_fields_set('patient', *DEFER_PATIENT_FIELDS)
        return self.defer(*deferred_doctor_field_set, *deferred_patient_field_set)

    def select_patient(self) -> 'PrescriptionQuerySet':
        return self.select_related('patient')

    def select_writer(self) -> 'PrescriptionQuerySet':
        return self.select_related('writer__user')

    def prefetch_doctor_file(self):
        return self.prefetch_related('doctor_files')

    def prefetch_file_prescription_with_files(self) -> 'PrescriptionQuerySet':
        return self.prefetch_related(Prefetch('file_prescriptions',
                                              queryset=FilePrescription.objects.prefetch_related('patient_files')
                                              ))


class PrescriptionManager(models.Manager):
    def get_queryset(self) -> 'PrescriptionQuerySet':
        return PrescriptionQuerySet(self.model, using=self._db). \
            annotate(user=F('writer_id'),
                     writer_name=concatenate_name('writer'),
                     patient_name=concatenate_name('patient'))

    def select_all(self) -> 'PrescriptionQuerySet':
        return self.get_queryset(). \
            select_writer(). \
            select_patient(). \
            order_by('-created_at'). \
            filter(deleted=False)

    def nested_all(self) -> 'PrescriptionQuerySet':
        return self.get_queryset(). \
            select_writer(). \
            select_patient(). \
            prefetch_file_prescription_with_files(). \
            filter(deleted=False)


"""
Prescription
- fields: id, description, status, created_at, updated_at, deleted, writer, patient, start_date, end_date 
"""


class Prescription(BasePrescription):
    writer = models.ForeignKey(Doctor, on_delete=models.DO_NOTHING)
    patient = models.ForeignKey(Patient, on_delete=models.DO_NOTHING, related_name='prescriptions')
    # files = models.FileField(upload_to=directory_path, null=True)

    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)

    objects = PrescriptionManager()

    # def __str__(self):
    #     return f'{self.writer.get_full_name()}-{self.patient.get_full_name()}-{str(self.created_at)}'

    def get_writer_name(self) -> str:
        return self.writer.get_full_name()


@receiver(post_save, sender=Prescription)
def create_file_prescription(sender, **kwargs):
    instance = kwargs['instance']
    start_date = instance.start_date
    end_date = instance.end_date

    if not start_date or not end_date:
        return None

    bulk_list = (FilePrescription(prescription_id=instance.id, day_number=day_number + 1)
                 for day_number in range((end_date - start_date).days))
    FilePrescription.objects.bulk_create(bulk_list)


class FilePrescriptionQuerySet(models.QuerySet):
    def filter_writer(self, writer_id: int) -> 'FilePrescriptionQuerySet':
        return self.filter(writer_id=writer_id)

    def filter_patient(self, patient_id: int) -> 'FilePrescriptionQuerySet':
        return self.filter(patient_id=patient_id)

    def defer_option_fields(self) -> 'FilePrescriptionQuerySet':
        deferred_doctor_field_set = get_defer_fields_set('writer', *DEFER_DOCTOR_FIELDS)
        deferred_patient_field_set = get_defer_fields_set('patient', *DEFER_PATIENT_FIELDS)
        return self.defer(*deferred_doctor_field_set, *deferred_patient_field_set)

    def prefetch_all(self) -> 'FilePrescriptionQuerySet':
        return self.prefetch_related('patient_files')

    def select_all(self) -> 'FilePrescriptionQuerySet':
        return self.select_related('prescription')


class FilePrescriptionManager(models.Manager):
    def get_queryset(self) -> 'FilePrescriptionQuerySet':
        return FilePrescriptionQuerySet(self.model, using=self._db). \
            annotate(user=F('prescription__writer_id'),
                     writer_name=concatenate_name('prescription__writer'),
                     patient=concatenate_name('prescription__patient'))

    def prefetch_all(self) -> 'FilePrescriptionQuerySet':
        return self.get_queryset().prefetch_all()

    def select_all(self) -> 'FilePrescriptionQuerySet':
        return self.get_queryset().select_all()


"""
FilePrescription
- fields: id, description, status, created_at, updated_at, deleted, prescription, day_number, active, checked 
"""


# Prescription과 DataFile을 잇는 중계 모델
class FilePrescription(BasePrescription):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='file_prescriptions')
    day_number = models.IntegerField()
    active = models.BooleanField(default=True)
    uploaded = models.BooleanField(default=False)

    objects = FilePrescriptionManager()

    def __str__(self) -> str:
        return f'{self.prescription.start_date}: {self.day_number}일'
