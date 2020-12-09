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

    def create_user(self, **kwargs):
        password = self._validate_password(kwargs)
        obj = BaseUser(**kwargs)
        obj.set_password(password)
        obj.save()
        return obj

    def _validate_password(self, validated_data):
        password = validated_data.pop('password')
        password2 = validated_data.pop('password2')
        if password == password2:
            return password
        return False


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

    def __str__(self):
        return f'{self.major}: {self.user.username}'


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
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True)  # m2m??
    age = models.PositiveIntegerField(default=0, blank=True)
    emergency_call = models.CharField(max_length=14, unique=True, blank=True, null=True)

    objects = PatientManager()

    def get_absolute_url(self):
        return reverse('accounts:patient:detail', kwargs={'pk': self.pk})
