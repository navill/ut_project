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
    first_name = serializers.CharField(read_only=True, help_text='사용자의 이름(ex: 길동)')
    last_name = serializers.CharField(read_only=True, help_text='사용자의 성(ex:홍)')
    gender = serializers.CharField(source='get_gender_display', read_only=True, help_text='성별(ex: MALE 또는 FEMALE)')
    address = serializers.CharField(help_text='사용자의 주소(ex: 광주광역시 ...)')
    phone = serializers.CharField(max_length=14, help_text='사용자의 전화번호(ex: 010-1111-1111)')

    def get_full_name(self, instance: Union[Doctor, Patient]) -> str:
        if hasattr(instance, 'full_name'):
            # return instance.full_name
            pass
        return instance.get_full_name()


class AccountSignupSerializer(AccountSerializer):
    first_name = serializers.CharField(help_text='사용자의 이름(ex: 길동)')  # todo: help_text 하드코딩 수정
    last_name = serializers.CharField(help_text='사용자의 성(ex: 홍)')
    gender = serializers.ChoiceField(choices=Gender.choices, help_text='성별(ex: MALE 또는 FEMALE)')


# BaseUser
class BaseUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True, help_text='계정 아이디로 사용될 이메일(ex: test@test.com)')

    class Meta:
        model = User
        fields = ['id', 'email']
        extra_kwargs = {'id': {'read_only': True}}


class BaseUserSignUpSerializer(BaseUserSerializer):
    email = serializers.EmailField(help_text='계정 아이디로 사용될 이메일(ex: test@test.com)',
                                   validators=[UniqueValidator(queryset=User.objects.all())])

    password = serializers.CharField(
        min_length=8,
        write_only=True,
        required=True,
        help_text='비밀번호(ex: xxxx1234)',
        style={'input_type': 'password', 'placeholder': 'Password'}
    )
    password2 = serializers.CharField(
        min_length=8,
        write_only=True,
        required=True,
        help_text='비밀번호 확인(ex: xxxx1234)',
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
    detail_url = serializers.HyperlinkedIdentityField(
        view_name='accounts:doctor-detail-update',
        lookup_field='pk',
        read_only=True,
        help_text='의사 프로필(detail) url'
    )
    major = serializers.CharField(source='major.name', read_only=True, help_text='의사 전공(ex: 심리학)')

    class Meta:
        model = Doctor
        fields = ['detail_url'] + DoctorFields.list_field
        extra_kwargs = {'user': {'help_text': '의사 계정 primary key(ex: 2)', 'read_only': True}}


class DoctorDetailSerializer(DoctorListSerializer):
    description = serializers.CharField(max_length=255, help_text='의사 간단 소개(ex: 정신과 의사 홍길동입니다.)')

    class Meta(DoctorListSerializer.Meta):
        fields = DoctorFields.detail_field


class DoctorSignUpSerializer(SignupSerializerMixin, AccountSignupSerializer):
    detail_url = serializers.HyperlinkedIdentityField(
        view_name='accounts:doctor-detail-update',
        lookup_field='pk',
        read_only=True,
        help_text='가입한 의사의 프로필 url'
    )
    user = BaseUserSignUpSerializer(help_text='의사 계정 정보 입력 필드(email, password1, password2)')
    major = serializers.PrimaryKeyRelatedField(queryset=Major.objects.all(), help_text='의사의 전공 primary key(ex: 1)')

    class Meta:
        model = Doctor
        fields = ['detail_url', 'gender', 'user', 'first_name', 'last_name', 'address', 'phone', 'description', 'major']
        extra_kwargs = {'description': {'help_text': '의사 간단 소개(ex: 정신과 의사 홍길동입니다.)'}}


# Patient
class PatientListSerializer(AccountSerializer):
    detail_url = serializers.HyperlinkedIdentityField(
        view_name='accounts:patient-detail-update',
        lookup_field='pk',
        read_only=True,
        help_text='환자 프로필 url'
    )

    class Meta:
        model = Patient
        fields = ['detail_url'] + PatientFields.list_field
        extra_kwargs = {
            'user': {'help_text': '환자 계정 primary key(ex: 5)', 'read_only': True},
            'doctor': {'help_text': '담당 의사 primary key(ex: 2)'},
            'age': {'help_text': '나이(ex: 30)'}
        }


class PatientDetailSerializer(PatientListSerializer):
    emergency_call = serializers.CharField(max_length=14, help_text='긴급 또는 보호자 번호(ex: 010-1111-2222)')

    class Meta(PatientListSerializer.Meta):
        fields = PatientFields.detail_field


class PatientSignUpSerializer(SignupSerializerMixin, AccountSignupSerializer):
    detail_url = serializers.HyperlinkedIdentityField(
        view_name='accounts:patient-detail-update',
        lookup_field='pk',
        read_only=True,
        help_text='환자 프로필 url'
    )
    user = BaseUserSignUpSerializer(help_text='환자 계정 정보 입력 필드(email, password1, password2)')
    doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.select_all(),
                                                help_text='담당 의사 primary key(ex: 2)')
    age = serializers.IntegerField(max_value=150, help_text='나이(ex: 30)')
    emergency_call = serializers.CharField(max_length=14, help_text='긴급 또는 보호자 번호(ex: 010-1111-2222)')

    class Meta:
        model = Patient
        fields = ['detail_url', 'user', 'first_name', 'last_name', 'gender', 'age', 'address', 'phone',
                  'emergency_call', 'doctor']


class AccountsTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user: User) -> Token:
        token = CustomRefreshToken.for_user(user)
        return token

    def validate(self, attrs):
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
