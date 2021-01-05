from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.forms import model_to_dict
from django.urls import reverse

from accounts.mixins.form_mixins import CommonUserQuerySetMixin
from hospitals.models import Major


class AccountsModel(models.Model):
    first_name = models.CharField(max_length=20, default='')
    last_name = models.CharField(max_length=20, default='')
    address = models.CharField(max_length=255, default='')
    phone = models.CharField(max_length=14, unique=True)

    class Meta:
        abstract = True


class BaseQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)


class BaseManager(BaseUserManager):
    def get_queryset(self):
        return BaseQuerySet(self.model, using=self._db).select_related('doctor')

    def get_child_model(self):
        queryset = self.get_queryset().prefetch_related('doctor')

    def all(self):
        return super().all()

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


# AbstractUser
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
        for user_model in AccountsModel.__subclasses__():
            child_attribute_name = user_model.__name__.lower()
            if hasattr(self, child_attribute_name):
                return getattr(self, child_attribute_name)
        return None


class DoctorQuerySet(CommonUserQuerySetMixin, models.QuerySet):
    pass


class DoctorManager(models.Manager):
    def get_queryset(self):
        return DoctorQuerySet(self.model, using=self._db).select_related('user')

    def all(self):
        active_doctor = self.get_queryset().active()
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
        return f'{self.major}: {self.user.email}'

    def get_full_name(self):
        return f'{self.first_name}_{self.last_name}'


class PatientQuerySet(CommonUserQuerySetMixin, models.QuerySet):
    pass


class PatientManager(models.Manager):
    def get_queryset(self):
        return PatientQuerySet(self.model, using=self._db).select_related('user')

    def all(self):
        active_patient = self.get_queryset().active()
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

    def get_full_name(self) -> str:
        return f'{self.first_name}_{self.last_name}'
