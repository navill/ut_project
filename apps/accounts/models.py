from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.urls import reverse

from accounts.mixins.form_mixins import CommonUserQuerySetMixin
from hospitals.models import Major

DEFER_ACCOUNTS_FIELDS = ('address', 'phone')
DEFER_BASEUSER_FIELDS = ('password', 'last_login', 'updated_at')
DEFER_DOCTOR_FIELDS = ('updated_at',) + DEFER_ACCOUNTS_FIELDS
DEFER_PATIENT_FIELDS = ('age', 'emergency_call') + DEFER_ACCOUNTS_FIELDS


class AccountsModel(models.Model):
    first_name = models.CharField(max_length=20, default='')
    last_name = models.CharField(max_length=20, default='')
    address = models.CharField(max_length=255, default='')
    phone = models.CharField(max_length=14, unique=True)

    class Meta:
        abstract = True

    def get_full_name(self) -> str:
        return f'{self.first_name}_{self.last_name}'


class BaseQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def defer_fields(self, *fields):
        return self.defer(*DEFER_BASEUSER_FIELDS, *fields)


class BaseManager(BaseUserManager):
    def get_queryset(self):
        return BaseQuerySet(self.model, using=self._db).select_related('doctor').select_related('patient')

    def all(self):
        return super().all().active()

    def create_user(self, email, password, **attributes):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(email=self.normalize_email(email), **attributes)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **attributes):
        self._set_superuser_status(attributes)
        # self._validate_superuser_status(attributes)
        return self.create_user(email=email, password=password, **attributes)

    def _set_superuser_status(self, attributes):
        attributes.setdefault('is_staff', True)
        attributes.setdefault('is_superuser', True)
        attributes.setdefault('is_active', True)

    def _validate_superuser_status(self, attributes):
        if attributes.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if attributes.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')


class BaseUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    token_expired = models.IntegerField(default=0)

    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = BaseManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'

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

    def get_child_account(self):
        if self.is_doctor:
            return self.doctor
        elif self.is_patient:
            return self.patient
        return None

    def get_child_username(self):
        if self.is_doctor:
            name = self.doctor.get_full_name()
        elif self.is_patient:
            name = self.patient.get_full_name()
        return name


class DoctorQuerySet(CommonUserQuerySetMixin, models.QuerySet):
    def defer_fields(self, *fields):
        defer_user_fields = self.generate_related_defer_fields(DEFER_BASEUSER_FIELDS)
        return super().defer_fields(*DEFER_DOCTOR_FIELDS, *defer_user_fields, *fields)


class DoctorManager(models.Manager):
    def get_queryset(self):
        return DoctorQuerySet(self.model, using=self._db).select_related('user').select_related('major')

    def all(self):
        active_doctor = self.get_queryset().filter_user_active()
        return active_doctor

    def with_patients(self):
        return self.all().prefetch_related('patients')


class Doctor(AccountsModel):
    user = models.OneToOneField(BaseUser, on_delete=models.CASCADE, primary_key=True)
    major = models.ForeignKey(Major, on_delete=models.CASCADE, related_name='doctor_major')
    description = models.CharField(max_length=255, default='', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = DoctorManager()

    def get_absolute_url(self):
        return reverse('accounts:doctor-detail-update', kwargs={'pk': self.pk})

    def __str__(self):
        return f'{self.major}: {self.get_full_name()}'


class PatientQuerySet(CommonUserQuerySetMixin, models.QuerySet):
    def defer_fields(self, *fields):
        defer_user_fields = self.generate_related_defer_fields(DEFER_BASEUSER_FIELDS)
        return super().defer_fields(*DEFER_PATIENT_FIELDS, *defer_user_fields, *fields)


class PatientManager(models.Manager):
    def get_queryset(self):
        return PatientQuerySet(self.model, using=self._db).select_related('user').select_related('doctor')

    def all(self):
        active_patient = self.get_queryset().filter_user_active()
        return active_patient


class Patient(AccountsModel):
    user = models.OneToOneField(BaseUser, on_delete=models.CASCADE, primary_key=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, related_name='patients')

    age = models.PositiveIntegerField(default=0)
    emergency_call = models.CharField(max_length=14, default='010')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PatientManager()

    def __str__(self):
        return self.get_full_name()

    def get_absolute_url(self) -> str:
        return reverse('accounts:patient-detail-update', kwargs={'pk': self.pk})
