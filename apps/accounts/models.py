from typing import Union, TYPE_CHECKING

from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.db.models import F
from django.db.models.functions import Concat
from django.urls import reverse

from accounts.mixins.form_mixins import CommonUserQuerySetMixin
from hospitals.models import Major

if TYPE_CHECKING:
    from django.db.models import QuerySet

DEFER_ACCOUNTS_FIELDS = ('address', 'phone')
DEFER_BASEUSER_FIELDS = ('password', 'last_login', 'created_at', 'updated_at', 'token_expired')
DEFER_DOCTOR_FIELDS = ('updated_at', 'description', 'created_at', 'updated_at') + DEFER_ACCOUNTS_FIELDS
DEFER_PATIENT_FIELDS = ('emergency_call', 'created_at', 'updated_at') + DEFER_ACCOUNTS_FIELDS


def get_defer_field_set(parent_field_name: str, *fields):
    fields = [f'{parent_field_name}__{field}' for field in fields]
    return fields


def concatenate_name():
    full_name = Concat(F('last_name'), F('first_name'))
    return full_name


class Gender(models.TextChoices):
    male = ('MALE', '남')
    female = ('FEMALE', '여')


class AccountsModel(models.Model):
    first_name = models.CharField(max_length=20, default='')
    last_name = models.CharField(max_length=20, default='')
    gender = models.CharField(max_length=7, choices=Gender.choices, default=Gender.male)
    address = models.CharField(max_length=255, default='')
    phone = models.CharField(max_length=14, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def get_full_name(self) -> str:
        return f'{self.first_name}_{self.last_name}'


class BaseQuerySet(models.QuerySet):
    def active(self) -> 'QuerySet':
        return self.filter(is_active=True)

    def defer_option_fields(self, *fields) -> 'QuerySet':
        return self.defer(*DEFER_BASEUSER_FIELDS, *fields)

    def select_all(self) -> 'QuerySet':
        return self.select_related('doctor').select_related('patient')

    def defer_unnecessary_fields(self) -> 'QuerySet':
        # deferred_doctor_fields = (f'doctor__{field}' for field in DEFER_DOCTOR_FIELDS)
        deferred_doctor_fields = get_defer_field_set(parent_field_name='doctor', *DEFER_DOCTOR_FIELDS)
        deferred_patient_fields = get_defer_field_set(parent_field_name='patient', *DEFER_PATIENT_FIELDS)
        return self.defer(*DEFER_BASEUSER_FIELDS, *deferred_doctor_fields, *deferred_patient_fields)


class BaseManager(BaseUserManager):
    def get_queryset(self) -> 'QuerySet':
        # request에서 user에 대한 select_related를 적용해야할 경우 authentication 수정 필요
        return BaseQuerySet(self.model, using=self._db).select_related('doctor').select_related('patient')

    def create_user(self, email, password, **attributes) -> 'BaseUser':
        if not email:
            raise ValueError('No email has been entered')

        user = self.model(email=self.normalize_email(email), **attributes)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **attributes) -> 'BaseUser':
        self._set_superuser_status(attributes)
        # self._validate_superuser_status(attributes)
        return self.create_user(email=email, password=password, **attributes)

    def select_all(self):
        return self.get_queryset().select_all()

    def _set_superuser_status(self, attributes):
        attributes.setdefault('is_staff', True)
        attributes.setdefault('is_superuser', True)
        attributes.setdefault('is_active', True)

    # def _validate_superuser_status(self, attributes):
    #     if attributes.get('is_staff') is not True:
    #         raise ValueError('Superuser must have is_staff=True.')
    #     if attributes.get('is_superuser') is not True:
    #         raise ValueError('Superuser must have is_superuser=True.')


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
    def is_doctor(self) -> bool:
        return hasattr(self, 'doctor')

    @property
    def is_patient(self) -> bool:
        return hasattr(self, 'patient')

    def __str__(self) -> str:
        return str(self.email)

    def set_token_expired(self, time: int):
        self.token_expired = time
        self.save()

    def get_child_account(self) -> Union['AccountsModel', None]:
        if self.is_doctor:
            return self.doctor
        elif self.is_patient:
            return self.patient
        return None

    def get_child_username(self) -> str:
        name = ''
        if self.is_doctor:
            name = self.doctor.get_full_name()
        elif self.is_patient:
            name = self.patient.get_full_name()
        return name


class DoctorQuerySet(CommonUserQuerySetMixin, models.QuerySet):
    def defer_option_fields(self, *fields: tuple) -> 'QuerySet':
        # deferred_user_fields = get_defer_field_set('user', DEFER_BASEUSER_FIELDS)
        deferred_user_fields = (f'user__{field}' for field in DEFER_BASEUSER_FIELDS)
        return self.defer(*DEFER_DOCTOR_FIELDS, *deferred_user_fields, *fields)


class DoctorManager(models.Manager):
    def get_queryset(self) -> 'QuerySet':
        return DoctorQuerySet(self.model, using=self._db). \
            annotate(full_name=concatenate_name())

    def select_all(self):
        return self.select_related('user').select_related('major').filter_user_active()

    def non_related_all(self):
        return self.defer('user', 'major')

    def with_patients(self):
        return self.all().prefetch_related('patients')


class Doctor(AccountsModel):
    user = models.OneToOneField(BaseUser, on_delete=models.CASCADE, primary_key=True)
    major = models.ForeignKey(Major, on_delete=models.CASCADE, related_name='doctor_major')
    description = models.CharField(max_length=255, default='', blank=True, null=True)

    objects = DoctorManager()

    def __str__(self):
        return f'{self.major.name}: {self.get_full_name()}'

    def get_absolute_url(self):
        return reverse('accounts:doctor-detail-update', kwargs={'pk': self.pk})


class PatientQuerySet(CommonUserQuerySetMixin, models.QuerySet):
    def defer_option_fields(self, *fields):
        defer_user_fields = (f'user__{field}' for field in DEFER_BASEUSER_FIELDS)
        defer_doctor_fields = (f'doctor__{field}' for field in DEFER_DOCTOR_FIELDS)
        return self.defer(*DEFER_PATIENT_FIELDS, *defer_doctor_fields, *defer_user_fields, *fields)

    def select_all(self):
        return self.select_related('user').select_related('doctor')


class PatientManager(models.Manager):
    def get_queryset(self):
        return PatientQuerySet(self.model, using=self._db).annotate(full_name=concatenate_name()).filter_user_active()

    def select_all(self):
        return self.get_queryset().select_related('user').select_related('doctor')


class Patient(AccountsModel):
    user = models.OneToOneField(BaseUser, on_delete=models.CASCADE, primary_key=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, related_name='patients')
    age = models.PositiveIntegerField(default=0)
    emergency_call = models.CharField(max_length=14, default='010')

    objects = PatientManager()

    def __str__(self):
        return self.get_full_name()

    def get_absolute_url(self) -> str:
        return reverse('accounts:patient-detail-update', kwargs={'pk': self.pk})
