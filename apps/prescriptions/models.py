from django.db import models
from django.db.models import F

from accounts.models import Patient, Doctor


class PrescriptionQuerySet(models.QuerySet):
    def filter_writer(self, writer: 'Doctor' = None):
        return self.filter(writer=writer)

    def filter_patient(self, patient: 'Patient' = None):
        return self.filter(user_patient=patient)


class PrescriptionManager(models.Manager):
    def get_queryset(self):
        return PrescriptionQuerySet(self.model, using=self._db).annotate(user=F('writer_id'))

    def all(self):
        return self.get_queryset().filter(deleted=False).order_by('-created_at')


class Prescription(models.Model):
    writer = models.ForeignKey(Doctor, on_delete=models.DO_NOTHING, null=True, related_name='prescription_by')
    user_patient = models.ForeignKey(Patient, on_delete=models.DO_NOTHING, null=True, related_name='prescription_to')
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    objects = PrescriptionManager()

    def __str__(self):
        return f'{self.user_patient}-{str(self.created_at)}'
