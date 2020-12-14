from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse

from accounts.mixins.form_mixins import CommonUserQuerySetMixin


class BaseQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)


class BaseManager(BaseUserManager):
    def get_queryset(self):
        return BaseQuerySet(self.model, using=self._db)

    def all(self):
        return super().all().active().order_by('-date_joined')

    def create_user(self, username, password, **extra_fields):
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(username=username, password=password, **extra_fields)


class BaseUser(AbstractUser):
    address = models.CharField(max_length=255, default='')
    phone = models.CharField(max_length=14, default='')
    date_updated = models.DateTimeField(auto_now=True)

    objects = BaseManager()

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def is_doctor(self):
        return hasattr(self, 'doctor')

    @property
    def is_patient(self):
        return hasattr(self, 'patient')

    def __str__(self):
        return self.username


class DoctorQuerySet(CommonUserQuerySetMixin, models.QuerySet):
    pass


class DoctorManager(models.Manager):
    def get_queryset(self):
        return DoctorQuerySet(self.model, using=self._db).select_related('user')

    def all(self):
        active_doctor = super().all().active()
        return active_doctor


class Doctor(models.Model):
    user = models.OneToOneField(BaseUser, on_delete=models.CASCADE, primary_key=True, related_name='doctor')
    department = models.CharField(max_length=255, default='')
    major = models.CharField(max_length=20, default='Psychiatrist')

    objects = DoctorManager()

    class Meta:
        permissions = (
            ("can_add_prescription", "Can write prescriptions"),
            ("can_change_prescription", "Can change prescriptions "),
            ("can_view_prescription", "Can view prescriptions "),
            # ("can_delete_prescription", "can delete prescriptions "),
        )

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
    family_doctor = models.ForeignKey(BaseUser, on_delete=models.SET_NULL, null=True,
                                      related_name='family_doctor')  # m2m??
    age = models.PositiveIntegerField(default=0, blank=True)
    emergency_call = models.CharField(max_length=14, unique=True, blank=True, null=True)

    objects = PatientManager()

    def __str__(self):
        return self.user.get_full_name()

    def get_absolute_url(self):
        return reverse('accounts:patient:detail', kwargs={'pk': self.pk})
