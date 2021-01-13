from django.db import models
from django.db.models import F
from django.db.models.functions import Concat

from accounts.models import Patient, Doctor, DEFER_PATIENT_FIELDS, DEFER_DOCTOR_FIELDS, DEFER_BASEUSER_FIELDS


def get_defer_fields_set(parent_field_name: str, *fields):
    return [f'{parent_field_name}__{field}' for field in fields]


def concatenate_name(target_field: str):
    full_name = Concat(F(f'{target_field}__first_name'), F(f'{target_field}__last_name'))
    return full_name


class PrescriptionQuerySet(models.QuerySet):
    def filter_writer(self, writer_id: int):
        return self.filter(writer_id=writer_id)

    def filter_patient(self, patient_id: int):
        return self.filter(patient_id=patient_id)

    def join_uploader(self, query_word: str):
        return self.select_related(query_word)

    def defer_fields(self):
        deferred_doctor_field_set = get_defer_fields_set('writer', *DEFER_DOCTOR_FIELDS)
        deferred_patient_field_set = get_defer_fields_set('patient', *DEFER_PATIENT_FIELDS)
        return self.defer(*deferred_doctor_field_set, *deferred_patient_field_set)


class PrescriptionManager(models.Manager):
    def get_queryset(self):
        return PrescriptionQuerySet(self.model, using=self._db).annotate(user=F('writer_id'),
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
        return f'prescription-{str(self.created_at)}'
