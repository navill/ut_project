from django.db import models
from django.db.models import F

from accounts.models import Patient, Doctor, DEFER_PATIENT_FIELDS, DEFER_DOCTOR_FIELDS
from prescriptions.api.utils import get_defer_fields_set, concatenate_name


class PrescriptionQuerySet(models.QuerySet):
    def filter_writer(self, writer_id: int):
        return self.filter(writer_id=writer_id)

    def filter_patient(self, patient_id: int):
        return self.filter(patient_id=patient_id)

    def join_uploader(self, query_word: str):
        return self.select_related(query_word)

    def defer_option_fields(self):
        deferred_doctor_field_set = get_defer_fields_set('writer', *DEFER_DOCTOR_FIELDS)
        deferred_patient_field_set = get_defer_fields_set('patient', *DEFER_PATIENT_FIELDS)
        return self.defer(*deferred_doctor_field_set, *deferred_patient_field_set)


class PrescriptionManager(models.Manager):
    def get_queryset(self):
        return PrescriptionQuerySet(self.model, using=self._db). \
            annotate(user=F('writer_id'),
                     writer_name=concatenate_name('writer'),
                     patient_name=concatenate_name('patient'))

    def select_all(self):
        return self.get_queryset().select_related('writer'). \
            select_related('patient'). \
            order_by('-created_at'). \
            filter(deleted=False)


class Prescription(models.Model):
    writer = models.ForeignKey(Doctor, on_delete=models.DO_NOTHING, related_name='prescription_by')
    patient = models.ForeignKey(Patient, on_delete=models.DO_NOTHING, related_name='prescription_to')
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    objects = PrescriptionManager()

    def __str__(self):
        return f'{self.writer.get_full_name()}-{self.patient.get_full_name()}-{str(self.created_at)}'

    def get_writer_name(self):
        return self.writer.get_full_name()


# Prescription과 DataFile을 잇는 중계 모델
class FilePrescription(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    description = models.TextField()
    deleted = models.BooleanField(default=False)
