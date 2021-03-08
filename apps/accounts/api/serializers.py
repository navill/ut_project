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
    first_name = serializers.CharField()  # todo: help_text 하드코딩 수정
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
