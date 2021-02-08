from typing import Union, TYPE_CHECKING, Tuple, Dict, List, Type, NoReturn

from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.db.models import Q, Prefetch, Max
from django.urls import reverse

from config.utils.utils import concatenate_name
from core.api.fields import PatientFields, DoctorFields
from hospitals.models import Major

if TYPE_CHECKING:
    from django.db.models import QuerySet


# DEFER_ACCOUNTS_FIELDS = ('address', 'phone')
# DEFER_BASEUSER_FIELDS = ('password', 'last_login', 'created_at', 'updated_at', 'token_expired')
# DEFER_DOCTOR_FIELDS = ('updated_at', 'description', 'created_at', 'updated_at') + DEFER_ACCOUNTS_FIELDS
# DEFER_PATIENT_FIELDS = ('emergency_call', 'created_at', 'updated_at') + DEFER_ACCOUNTS_FIELDS


def get_defer_field_set(parent_field_name: str, *fields: Tuple[str]) -> List[str]:
    fields = [f'{parent_field_name}__{field}' for field in fields]
    return fields


class CommonUserQuerySet(models.QuerySet):
    def filter_user_active(self) -> Type['QuerySet']:
        return self.filter(user__is_active=True)

    def filter_doctor(self) -> Type['QuerySet']:
        return self.filter(Q(is_doctor=True) & Q(is_patient=False))

    def filter_patient(self) -> Type['QuerySet']:
        return self.filter(Q(is_doctor=False) & Q(is_patient=True))


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
        return f'{self.first_name} {self.last_name}'


class BaseQuerySet(models.QuerySet):
    def active(self) -> 'BaseQuerySet':
        return self.filter(is_active=True)

    # def defer_option_fields(self, *fields: Tuple[str]) -> 'BaseQuerySet':
    #     return self.defer(*DEFER_BASEUSER_FIELDS, *fields)

    def select_all(self) -> 'BaseQuerySet':
        return self.select_related('doctor').select_related('patient')

    # def defer_unnecessary_fields(self) -> 'BaseQuerySet':
    #     # deferred_doctor_fields = (f'doctor__{field}' for field in DEFER_DOCTOR_FIELDS)
    #     deferred_doctor_fields = get_defer_field_set(parent_field_name='doctor', *DEFER_DOCTOR_FIELDS)
    #     deferred_patient_fields = get_defer_field_set(parent_field_name='patient', *DEFER_PATIENT_FIELDS)
    #     return self.defer(*DEFER_BASEUSER_FIELDS, *deferred_doctor_fields, *deferred_patient_fields)


class BaseManager(BaseUserManager):
    def get_queryset(self) -> 'BaseQuerySet':
        # request에서 user에 대한 select_related를 적용해야할 경우 authentication 수정 필요
        return BaseQuerySet(self.model, using=self._db).select_related('doctor').select_related('patient')

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
        self._set_superuser_status(attributes)
        return self.create_user(email=email, password=password, **attributes)

    def _set_superuser_status(self, attributes) -> NoReturn:
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

    def set_token_expired(self, time: int) -> NoReturn:
        self.token_expired = time
        self.save()

    def get_child_account(self) -> Union['Doctor', 'Patient', None]:
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


class DoctorQuerySet(CommonUserQuerySet):
    # def defer_option_fields(self, *fields: str) -> 'DoctorQuerySet':
    #     # deferred_user_fields = get_defer_field_set('user', DEFER_BASEUSER_FIELDS)
    #     deferred_user_fields = (f'user__{field}' for field in DEFER_BASEUSER_FIELDS)
    #     return self.defer(*DEFER_DOCTOR_FIELDS, *deferred_user_fields, *fields)

    def prefetch_all(self):
        return self.prefetch_related('patients')

    def select_all(self):
        return self.select_related('user').select_related('major')

    def nested_all(self):
        return self.select_all().prefetch_all()

    # todo: 하드 코딩 -> 소프트 코딩으로 변경할 것
    def only_list(self, *others: Tuple[str]):
        fields = DoctorFields.list_field + others
        return self.only(*fields)

    def only_detail(self, *others: Tuple[str]):
        fields = DoctorFields.detail_field + others
        return self.only(*fields)


class DoctorManager(CommonUserManager):
    def get_queryset(self) -> DoctorQuerySet:
        return DoctorQuerySet(self.model, using=self._db). \
            annotate(full_name=concatenate_name()).filter_user_active()

    def non_related_all(self) -> DoctorQuerySet:
        return self.defer('user', 'major')


class Doctor(AccountsModel):
    user = models.OneToOneField(BaseUser, on_delete=models.CASCADE, primary_key=True)
    major = models.ForeignKey(Major, on_delete=models.CASCADE, related_name='doctors')
    description = models.CharField(max_length=255, default='', blank=True, null=True)

    objects = DoctorManager()

    def __str__(self) -> str:
        return f'{self.get_full_name()}'

    def get_absolute_url(self) -> str:
        return reverse('accounts:doctor-detail-update', kwargs={'pk': self.pk})


class PatientQuerySet(CommonUserQuerySet):
    # def defer_option_fields(self, *fields: Tuple[str, ...]) -> 'PatientQuerySet':
    #     defer_user_fields = (f'user__{field}' for field in DEFER_BASEUSER_FIELDS)
    #     defer_doctor_fields = (f'doctor__{field}' for field in DEFER_DOCTOR_FIELDS)
    #     return self.defer(*DEFER_PATIENT_FIELDS, *defer_doctor_fields, *defer_user_fields, *fields)

    def with_latest_prescription(self) -> 'PatientQuerySet':
        return self.filter(prescriptions__checked=False).annotate(latest_prescription_id=Max('prescriptions__id'))

    def prefetch_prescription_with_writer(self) -> 'PatientQuerySet':
        from prescriptions.models import Prescription

        return self.prefetch_related(Prefetch('prescriptions__writer', queryset=Prescription.objects.select_all()))

    def prefetch_prescription(self, prefetch: 'Prefetch' = None) -> 'PatientQuerySet':
        if prefetch:
            query = self.prefetch_related(prefetch)
        else:
            query = self.prefetch_related('prescriptions')
        return query

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

    def nested_all(self):
        return self.select_all().prefetch_all()

    # todo: 하드 코딩 -> 소프트 코딩으로 변경할 것
    def only_list(self, *others: Tuple[str]):
        fields = PatientFields.list_field + others
        return self.only(*fields)

    def only_detail(self, *others: Tuple[str]):
        fields = PatientFields.detail_field + others
        return self.only(*fields)


class PatientManager(CommonUserManager):
    def get_queryset(self) -> PatientQuerySet:
        return PatientQuerySet(self.model, using=self._db). \
            annotate(full_name=concatenate_name(),
                     doctor_name=concatenate_name('doctor')). \
            filter_user_active()


class Patient(AccountsModel):
    user = models.OneToOneField(BaseUser, on_delete=models.CASCADE, primary_key=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, related_name='patients')
    # birth = models.DateField()  # -> annotate를 이용해 age 필드 생성
    age = models.PositiveIntegerField(default=0)
    emergency_call = models.CharField(max_length=14, default='010')

    objects = PatientManager()

    def __str__(self) -> str:
        return f'이름: {self.get_full_name()}, 나이: {self.age}, 성별: {self.get_gender_display()}'

    def get_absolute_url(self) -> str:
        return reverse('accounts:patient-detail-update', kwargs={'pk': self.pk})
