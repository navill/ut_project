from typing import Union, Dict, AnyStr, NoReturn

from django.contrib.auth import get_user_model
from django.db import transaction
from django.urls import reverse
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import Token

from accounts.api.authentications import CustomRefreshToken
from accounts.api.mixins import SignupSerializerMixin, RefreshBlacklistMixin
from accounts.models import Doctor, Patient, Gender
from core.api.fields import DoctorFields, PatientFields
from hospitals.models import Major

User = get_user_model()


class AccountSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    gender = serializers.CharField(source='get_gender_display', read_only=True)
    address = serializers.CharField()
    phone = serializers.CharField(max_length=14)

    def get_full_name(self, instance: Union[Doctor, Patient]) -> str:
        if hasattr(instance, 'full_name'):
            pass
        return instance.get_full_name()


class AccountSignupSerializer(AccountSerializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    gender = serializers.ChoiceField(choices=Gender.choices)


# BaseUser
class BaseUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email']
        extra_kwargs = {'id': {'read_only': True}}


class BaseUserSignUpSerializer(BaseUserSerializer):
    email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all())])

    password = serializers.CharField(
        min_length=8,
        write_only=True,
        required=True,
        style={'input_type': 'password', 'placeholder': 'Password'}
    )
    password2 = serializers.CharField(
        min_length=8,
        write_only=True,
        required=True,
        style={'input_type': 'password', 'placeholder': 'Confirm Password'}
    )

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + ['password', 'password2']

    def validate(self, data: Dict[str, AnyStr]) -> Dict[str, AnyStr]:
        self._check_matched_password(data)
        return data

    def _check_matched_password(self, data: Dict[str, AnyStr]) -> NoReturn:
        if data.get('password') != data.get('password2'):
            raise serializers.ValidationError("Those passwords do not match.")
        data.pop('password2')


# Doctor
class DoctorListSerializer(AccountSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='accounts:doctor-detail',
        lookup_field='pk',
        read_only=True,
    )
    major = serializers.CharField(source='major.name', read_only=True)

    class Meta:
        model = Doctor
        fields = ['url'] + DoctorFields.list_field


class DoctorDetailSerializer(DoctorListSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='accounts:doctor-update',
        lookup_field='pk',
        read_only=True,
    )
    description = serializers.CharField(max_length=255)

    class Meta(DoctorListSerializer.Meta):
        fields = ['url'] + DoctorFields.detail_field


class DoctorUpdateSerializer(DoctorDetailSerializer):
    class Meta:
        model = Doctor
        fields = ['address', 'phone', 'description']


class DoctorSignUpSerializer(SignupSerializerMixin, AccountSignupSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='accounts:doctor-detail',
        lookup_field='pk',
        read_only=True,
    )
    user = BaseUserSignUpSerializer()
    major = serializers.PrimaryKeyRelatedField(queryset=Major.objects.all())

    class Meta:
        model = Doctor
        fields = ['url', 'gender', 'user', 'first_name', 'last_name', 'address', 'phone', 'description', 'major']


# 의사를 선택해야할 때
# 환자 계정 생성
#   1. 병원 -> 부서 -> 전공 -> 의사 선택: Hospital.choice_fields 사용
#       => /choices/doctors?major_id=1  # major_id는 병원마다 고유하기 때문에 의사를 최종 선택할 때 사용
#   2. 의사 이름으로 검색: 병원, 부서, 전공이 출력되고 사용자가 선택
class DoctorChoiceSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    gender = serializers.CharField(source='get_gender_display')
    major_name = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()
    medical_center_name = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        fields = ['user_id', 'major_id', 'full_name', 'gender', 'major_name', 'department_name', 'medical_center_name']

    def get_major_name(self, instance):
        return instance.major_name

    def get_full_name(self, instance):
        return instance.full_name

    def get_department_name(self, instance):
        return instance.department_name

    def get_medical_center_name(self, instance):
        return instance.medical_center_name


# Patient
class PatientListSerializer(AccountSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='accounts:patient-detail',
        lookup_field='pk',
        read_only=True,
    )
    age = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = ['url'] + PatientFields.list_field

    def get_age(self, instance: Patient) -> int:
        return instance.age


class PatientDetailSerializer(PatientListSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='accounts:patient-update',
        lookup_field='pk',
        read_only=True,
    )
    emergency_call = serializers.CharField(max_length=14)

    class Meta(PatientListSerializer.Meta):
        fields = ['url'] + PatientFields.detail_field


class PatientUpdateSerializer(PatientDetailSerializer):
    class Meta:
        model = Patient
        fields = ['address', 'phone', 'emergency_call']


class PatientSignUpSerializer(SignupSerializerMixin, AccountSignupSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='accounts:patient-detail',
        lookup_field='pk',
        read_only=True,
    )
    user = BaseUserSignUpSerializer()
    doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.select_all())
    birth = serializers.DateField()
    emergency_call = serializers.CharField(max_length=14)

    class Meta:
        model = Patient
        fields = ['url', 'user', 'first_name', 'last_name', 'gender', 'birth', 'address', 'phone',
                  'emergency_call', 'doctor']


# 환자를 선택해야할 때
# 질병에 따른 환자 리스트 출력(질병코드를 이용한 필터(질병 코드는 아직 미구현))
#     /choices/patients/disease_code=x1234
# 의사가 담당하고 있는 환자 리스트
#     /choices/patients/doctor_id=2
#
class PatientChoiceSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    gender = serializers.CharField(source='get_gender_display')
    age = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = ['user_id', 'full_name', 'doctor_id', 'doctor_name', 'gender', 'age']

    def get_full_name(self, instance):
        return instance.full_name

    def get_age(self, instance):
        return instance.age

    def get_doctor_name(self, instance):
        return instance.doctor_name


class AccountsTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user: User) -> Token:
        token = CustomRefreshToken.for_user(user)
        return token

    def validate(self, attrs: Dict[str, str]) -> Dict[str, str]:
        data = super(AccountsTokenSerializer, self).validate(attrs)
        self._add_next_url(data)
        return data

    def _add_next_url(self, data: Dict[str, str]):
        if self.user.is_doctor:
            data['main_url'] = reverse('core-api:doctors:detail', kwargs={'pk': self.user.id})
        elif self.user.is_patient:
            data['main_url'] = reverse('core-api:patients:main', kwargs={'pk': self.user.id})


class AccountsTokenRefreshSerializer(RefreshBlacklistMixin, TokenRefreshSerializer):
    @transaction.atomic
    def validate(self, attrs: Dict[str, Union[AnyStr, int]]) -> Dict[str, Union[AnyStr, int]]:
        refresh_obj = CustomRefreshToken(attrs['refresh'])
        data = {'access': str(refresh_obj.access_token)}
        access_token_exp = refresh_obj.access_token.payload['exp']

        self.try_blacklist(refresh=refresh_obj)
        self.set_refresh_payload(refresh=refresh_obj)
        self.set_user_expired_to(epoch_time=access_token_exp)

        refresh_token = str(refresh_obj)
        data['refresh'] = refresh_token

        return data
