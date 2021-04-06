from typing import TYPE_CHECKING, Tuple, Dict, List, Type, NoReturn

from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.db.models import Q, Prefetch, Max, F
from django.http import QueryDict
from django.urls import reverse
from rest_framework.exceptions import ValidationError

from accounts.database_function import CalculateAge
from config.utils.utils import concatenate_name
from core.api.fields import PatientFields, DoctorFields
from hospitals.models import Major, MedicalCenter

if TYPE_CHECKING:
    from django.db.models import QuerySet


class CommonUserQuerySet(models.QuerySet):
    def is_active(self) -> Type['QuerySet']:
        return self.filter(user__is_active=True)

    # [Deprecated]
    # def is_doctor(self) -> Type['QuerySet']:
    #     return self.filter(Q(is_doctor=True) & Q(is_patient=False))
    #
    # def is_patient(self) -> Type['QuerySet']:
    #     return self.filter(Q(is_doctor=False) & Q(is_patient=True))


class CommonUserManager(models.Manager):
    def select_all(self) -> Type['CommonUserQuerySet']:
        return self.get_queryset().select_all()

    def prefetch_all(self) -> Type['CommonUserQuerySet']:
        return self.get_queryset().prefetch_all()

    def nested_all(self) -> Type['CommonUserQuerySet']:
        return self.get_queryset().select_all().prefetch_all()


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
        return f'{self.first_name}{self.last_name}'


class BaseQuerySet(models.QuerySet):
    def active(self) -> 'BaseQuerySet':
        return self.filter(is_active=True)

    def select_all(self) -> 'BaseQuerySet':
        return self.select_related('doctor').select_related('patient')


class BaseManager(BaseUserManager):
    def get_queryset(self) -> 'BaseQuerySet':
        # authentication에 필요한 최소 필드(password는 제외: 보안상)
        return BaseQuerySet(self.model, using=self._db).only('id', 'email', 'doctor__user_id',
                                                             'patient__user_id')

    def select_all(self) -> 'BaseQuerySet':
        return self.get_queryset().select_all()

    def create_user(self, email, password, **attributes: Dict[str, str]) -> 'BaseUser':
        if not email:
            raise ValueError('No email has been entered')

        user = self.model(email=self.normalize_email(email), **attributes)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **attributes: Dict[str, str]) -> 'BaseUser':
        self._set_superuser_fields(attributes)
        return self.create_user(email=email, password=password, **attributes)

    def _set_superuser_fields(self, attributes) -> NoReturn:
        attributes.setdefault('is_staff', True)
        attributes.setdefault('is_superuser', True)
        attributes.setdefault('is_active', True)


class UserType:
    def __init__(self, group_name: str):
        self._doctor = False
        self._patient = False
        self.group_name = group_name
        self.initialize()

    @property
    def doctor(self) -> bool:
        return self._doctor

    @doctor.setter
    def doctor(self, is_doctor: bool) -> NoReturn:
        self._doctor = is_doctor
        self.validate_type()

    @property
    def patient(self) -> bool:
        return self._patient

    @patient.setter
    def patient(self, is_patient: bool) -> NoReturn:
        self._patient = is_patient
        self.validate_type()

    def validate_type(self) -> NoReturn:
        if self.doctor and self.patient:
            self.reset_user_type()
            raise ValidationError('invalid user type')

    def validate_group(self) -> NoReturn:
        if self.group_name not in ['doctor', 'patient']:
            raise ValidationError('invalid group name')

    def initialize(self):
        self.validate_group()
        setattr(self, self.group_name, True)
        self.validate_type()

    def reset_user_type(self) -> NoReturn:
        self.doctor = False
        self.patient = False


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

    user_type = None

    # [Deprecated]
    # @property
    # def is_doctor(self) -> bool:
    #     return self.groups.filter(name='doctor').exists()
    #
    # @property
    # def is_doctor(self) -> bool:
    #     return hasattr(self, 'doctor')
    #
    # @property
    # def is_patient(self) -> bool:
    #     return self.user_type.patient

    def __str__(self) -> str:
        return str(self.email)

    def set_token_expired(self, time: int) -> NoReturn:
        self.token_expired = time
        self.save()

    def set_user_type(self, group_name: str):
        self.user_type = UserType(group_name)  # Has-a(composition)

    # [Deprecated]
    # def get_child_account(self) -> Union['Doctor', 'Patient', None]:
    #     if self.is_doctor:
    #         return self.doctor
    #     elif self.is_patient:
    #         return self.patient
    #     return None
    #
    # def get_child_username(self) -> str:
    #     name = ''
    #     if self.is_doctor:
    #         name = self.doctor.get_full_name()
    #     elif self.is_patient:
    #         name = self.patient.get_full_name()
    #     return name


class DoctorQuerySet(CommonUserQuerySet):
    def prefetch_all(self):
        return self.prefetch_related('patients')

    def select_all(self):
        return self.select_related('user').select_related('major')

    def nested_all(self):
        return self.select_all().prefetch_all()

    def only_list(self, *others: Tuple[str]):
        fields = DoctorFields.list_field + others
        return self.only(*fields)

    def only_detail(self, *others: Tuple[str]):
        fields = DoctorFields.detail_field + others
        return self.only(*fields)


class DoctorManager(CommonUserManager):
    def get_queryset(self) -> DoctorQuerySet:
        return DoctorQuerySet(self.model, using=self._db). \
            annotate(full_name=concatenate_name()).is_active()

    def non_related_all(self) -> DoctorQuerySet:
        return self.defer('user', 'major')

    def choice_fields(self) -> DoctorQuerySet:
        return self.only('user_id', 'major_id', 'first_name', 'last_name', 'gender'). \
            annotate(major_name=F('major__name'), department_name=F('major__department__name'),
                     medical_center_name=F('major__department__medical_center__name'))


class Doctor(AccountsModel):
    user = models.OneToOneField(BaseUser, on_delete=models.CASCADE, primary_key=True)
    major = models.ForeignKey(Major, on_delete=models.CASCADE, related_name='doctors')
    description = models.CharField(max_length=255, default='', blank=True, null=True)

    objects = DoctorManager()

    def __str__(self) -> str:
        return self.get_full_name()

    def get_absolute_url(self) -> str:
        return reverse('accounts:doctor-detail-update', kwargs={'pk': self.pk})


class PatientQuerySet(CommonUserQuerySet):
    def with_latest_prescription(self) -> 'PatientQuerySet':
        return self.filter(prescriptions__checked=False).annotate(latest_prescription_id=Max('prescriptions__id'))

    def prefetch_prescription_with_writer(self) -> 'PatientQuerySet':
        from prescriptions.models import Prescription  # models에 그냥 import할 경우 import error
        return self.prefetch_related(Prefetch('prescriptions__writer', queryset=Prescription.objects.select_all()))

    def prefetch_prescription(self, prefetch: 'Prefetch' = 'prescription') -> 'PatientQuerySet':
        return self.prefetch_related(prefetch)

    def prefetch_prescription_with_patient(self) -> 'PatientQuerySet':
        return self.prefetch_related('prescriptions__patient')

    def prefetch_prescription_with_doctor_file(self) -> 'PatientQuerySet':
        return self.prefetch_related('prescriptions__doctor_files')

    def prefetch_prescription_with_file_prescriptions(self) -> 'PatientQuerySet':
        return self.prefetch_related('prescriptions__file_prescriptions')

    def select_all(self) -> 'PatientQuerySet':
        return self.select_related('doctor__major')

    def prefetch_all(self) -> 'PatientQuerySet':
        return self.prefetch_prescription_with_writer(). \
            prefetch_prescription_with_patient(). \
            prefetch_prescription_with_doctor_file(). \
            prefetch_prescription_with_file_prescriptions()

    def nested_all(self) -> 'PatientQuerySet':
        return self.select_all().prefetch_all()

    def only_list(self, *others: List[str]) -> 'PatientQuerySet':
        fields = PatientFields.list_field + list(others)
        return self.only(*fields)

    def only_detail(self, *others: List[str]) -> 'PatientQuerySet':
        fields = PatientFields.detail_field + list(others)
        return self.only(*fields)

    def set_age(self) -> 'PatientQuerySet':
        return self.annotate(age=CalculateAge('birth'))  # select에서 Function 실행

    def add_extra_for_age(self, expression: str) -> 'PatientQuerySet':
        if expression:
            return self.extra(where=[expression])  # where에서 Function 실행
        return self


class PatientManager(CommonUserManager):
    def get_queryset(self) -> PatientQuerySet:
        return PatientQuerySet(self.model, using=self._db). \
            annotate(full_name=concatenate_name(),
                     doctor_name=concatenate_name('doctor')). \
            is_active(). \
            set_age()

    def choice_fields(self) -> PatientQuerySet:
        return self.only('user_id', 'doctor__first_name', 'doctor__last_name', 'gender')


class Patient(AccountsModel):
    user = models.OneToOneField(BaseUser, on_delete=models.CASCADE, primary_key=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.DO_NOTHING, related_name='patients')
    birth = models.DateField()
    emergency_call = models.CharField(max_length=14, default='010')

    objects = PatientManager()

    def __str__(self) -> str:
        return self.get_full_name()

    def get_absolute_url(self) -> str:
        return reverse('accounts:patient-detail-update', kwargs={'pk': self.pk})


# m2m patient to doctor(보류)
class M2MPatient(AccountsModel):
    user = models.OneToOneField(BaseUser, on_delete=models.CASCADE, primary_key=True)
    medical_center = models.ManyToManyField(MedicalCenter, related_name='patients_from')
    doctor = models.ManyToManyField(Doctor, related_name='patients_by')
    birth = models.DateField()
    emergency_call = models.CharField(max_length=14, default='010')

    objects = PatientManager()

    def get_absolute_url(self) -> str:
        return reverse('accounts:patient-detail-update', kwargs={'pk': self.pk})
