from django.db import models

# Create your models here.
from accounts.models import Patient, Doctor


class Prescription(models.Model):
    writer = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, related_name='prescription_by')
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, related_name='prescription_to')

    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


