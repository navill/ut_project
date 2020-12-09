from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse

from accounts.mixins.form_mixins import CommonUserQuerySetMixin


class BaseQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)


class BaseManager(BaseUserManager):
    def get_by_natural_key(self, username):
        return self.get(username=username)

    def get_queryset(self):
        return BaseQuerySet(self.model, using=self._db)

    def all(self):
        return super().all().active().order_by('-date_joined')


class BaseUser(AbstractUser):
    address = models.CharField(max_length=255, default='')
    phone = models.CharField(max_length=14, default='')
    date_updated = models.DateTimeField(auto_now=True)

    objects = BaseManager()

    def get_full_name(self):
        return str(self.last_name + self.first_name)

    @property
    def is_doctor(self):
        return hasattr(self, 'doctor')

    @property
    def is_patient(self):
        return hasattr(self, 'patient')


class DoctorQuerySet(CommonUserQuerySetMixin, models.QuerySet):
    pass


class DoctorManager(models.Manager):
    def get_queryset(self):
        return DoctorQuerySet(self.model, using=self._db).select_related('user')

    def all(self):
        active_doctor = super().all().active()
        return active_doctor


class Doctor(models.Model):
    user = models.OneToOneField(BaseUser, on_delete=models.CASCADE, primary_key=True)
    department = models.CharField(max_length=255, default='')
    major = models.CharField(max_length=20, default='Psychiatrist')

    objects = DoctorManager()

    def get_absolute_url(self):
        return reverse('accounts:doctor:detail', kwargs={'pk': self.pk})


class PatientQuerySet(CommonUserQuerySetMixin, models.QuerySet):
    pass


class PatientManager(models.Manager):
    def get_queryset(self):
        return PatientQuerySet(self.model, using=self._db).select_related('user')

    def all(self):
        active_patient = super().all().active()
        return active_patient


class Patient(models.Model):
    user = models.OneToOneField(BaseUser, on_delete=models.CASCADE, primary_key=True)
    age = models.IntegerField(default=0)
    emergency_call = models.CharField(max_length=14, default='0')
    prescription = models.TextField(default='')

    objects = PatientManager()

    def get_absolute_url(self):
        return reverse('accounts:patient:detail', kwargs={'pk': self.pk})
