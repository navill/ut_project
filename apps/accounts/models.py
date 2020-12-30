from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.urls import reverse

from accounts.mixins.form_mixins import CommonUserQuerySetMixin
from hospitals.models import Major


class BaseQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)


class BaseManager(BaseUserManager):
    def get_queryset(self):
        return BaseQuerySet(self.model, using=self._db)

    def all(self):
        return super().all()

    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_('Users must have an email address'))

        user = self.model(
            email=self.normalize_email(email),
            **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email=email, password=password, **extra_fields)


# AbstractUser
class BaseUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    token_expired = models.IntegerField(default=0)

    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    # groups =

    objects = BaseManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'

    # @property
    # def get_full_name(self):
    #     return f'{self.first_name} {self.last_name}'

    @property
    def is_doctor(self):
        return hasattr(self, 'doctor')

    @property
    def is_patient(self):
        return hasattr(self, 'patient')

    def __str__(self):
        return self.email

    def set_token_expired(self, time: int):
        self.token_expired = time
        self.save()


class DoctorQuerySet(CommonUserQuerySetMixin, models.QuerySet):
    pass


class DoctorManager(models.Manager):
    def get_queryset(self):
        return DoctorQuerySet(self.model, using=self._db).select_related('user')

    def all(self):
        active_doctor = super().all().filter(user__is_active=True)
        return active_doctor

    def patients(self):
        return self.all().prefetch_related('patients')


class Doctor(models.Model):
    user = models.OneToOneField(BaseUser, on_delete=models.CASCADE, primary_key=True)
    first_name = models.CharField(max_length=20, default='')
    last_name = models.CharField(max_length=20, default='')
    address = models.CharField(max_length=255, default='')
    phone = models.CharField(max_length=14, default='')

    major = models.ForeignKey(Major, on_delete=models.CASCADE, related_name='doctor_major')
    description = models.CharField(max_length=255, default='', blank=True, null=True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    objects = DoctorManager()

    def get_absolute_url(self):
        return reverse('accounts:doctor-detail-update', kwargs={'pk': self.pk})

    def __str__(self):
        return f'{self.major}: {self.user.email}'

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'


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
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, related_name='patients')  # m2m??

    first_name = models.CharField(max_length=20, default='')
    last_name = models.CharField(max_length=20, default='')
    address = models.CharField(max_length=255, default='')
    phone = models.CharField(max_length=14, default='')

    age = models.PositiveIntegerField(default=0)
    emergency_call = models.CharField(max_length=14, default='010')

    objects = PatientManager()

    # def __str__(self):
    #     return self.full_name

    def get_absolute_url(self):
        return reverse('accounts:patient-detail-update', kwargs={'pk': self.pk})

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'
