from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer

from accounts.api.authentications import CustomRefreshToken
from accounts.api.mixins import UserCreateMixin, RefreshBlacklistMixin
from accounts.models import Doctor, Patient
from hospitals.api.serializers import DefaultMajorSerializer
from hospitals.models import Major

if TYPE_CHECKING:
    from accounts.models import BaseUser

User = get_user_model()


class RawAccountSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    address = serializers.CharField()
    phone = serializers.CharField()

    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()


# BaseUser

class DefaultBaseUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)

    class Meta:
        model = User
        fields = ['email']


class BaseUserSerializer(DefaultBaseUserSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", read_only=True)
    last_login = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", read_only=True)

    class Meta(DefaultBaseUserSerializer.Meta):
        fields = DefaultBaseUserSerializer.Meta.fields + ['created_at', 'updated_at', 'last_login']


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

    def validate(self, data):
        self._check_matched_password(data)
        return data

    def _check_matched_password(self, data):
        if data.get('password') != data.get('password2'):
            raise serializers.ValidationError("Those passwords do not match.")
        data.pop('password2')


# Doctor
class RawDoctorSerializer(RawAccountSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    major = serializers.PrimaryKeyRelatedField(queryset=Major.objects.all())
    description = serializers.CharField()


class DefaultDoctorSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='accounts:doctor-detail-update',
        lookup_field='pk',
        read_only=True
    )
    user = DefaultBaseUserSerializer(read_only=True)
    major = DefaultMajorSerializer(read_only=True)

    class Meta:
        model = Doctor
        fields = ['url', 'user', 'first_name', 'last_name', 'major']

    def get_user_email(self, instance):
        return instance.user.email

    def get_major_name(self, instance):
        return instance.major.name


class DoctorSerializer(DefaultDoctorSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    major = serializers.PrimaryKeyRelatedField(read_only=True)
    user_email = serializers.SerializerMethodField()
    major_name = serializers.SerializerMethodField()

    class Meta(DefaultDoctorSerializer.Meta):
        # fields = DefaultDoctorSerializer.Meta.fields + ['user_email', 'major_name', 'address', 'phone', 'description',
        #                                                 'created_at', 'updated_at']
        fields = ['url', 'user', 'user_email', 'major', 'major_name', 'first_name', 'last_name', 'address', 'phone',
                  'description', 'created_at', 'updated_at']


class DoctorListSerializer(DefaultDoctorSerializer):
    user = DefaultBaseUserSerializer(read_only=True)

    class Meta(DefaultDoctorSerializer.Meta):
        fields = DefaultDoctorSerializer.Meta.fields


class DoctorRetrieveSerializer(DoctorSerializer):
    class Meta(DoctorSerializer.Meta):
        fields = DoctorSerializer.Meta.fields
        read_only_fields = ['first_name', 'last_name']


class DoctorSignUpSerializer(UserCreateMixin, DoctorSerializer):
    user = BaseUserSignUpSerializer()


# Patient
class RawPatientSerializer(RawAccountSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())
    age = serializers.IntegerField()
    emergency_call = serializers.IntegerField()


class DefaultPatientSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='accounts:patient-detail-update',
        lookup_field='pk',
        read_only=True
    )
    user = DefaultBaseUserSerializer()
    doctor = DefaultDoctorSerializer()

    class Meta:
        model = Patient
        # fields = ['url', 'user', 'first_name', 'last_name', 'address', 'phone', 'major', 'description', 'created_at',
        #           'updated_at']
        fields = ['url', 'doctor', 'user', 'first_name', 'last_name']

    def get_user_email(self, instance):
        return instance.user.email

    def get_doctor_name(self, instance):
        return instance.doctor.get_full_name()


class PatientSerializer(DefaultPatientSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    doctor = serializers.PrimaryKeyRelatedField(read_only=True)
    user_email = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()

    class Meta(DefaultPatientSerializer.Meta):
        # fields = DefaultDoctorSerializer.Meta.fields + ['user_email', 'major_name', 'address', 'phone', 'description',
        #                                                 'created_at', 'updated_at']
        fields = ['url', 'doctor', 'doctor_name', 'user', 'user_email', 'first_name', 'last_name', 'address', 'phone',
                  'age', 'emergency_call', 'created_at', 'updated_at']


class PatientListSerailizer(DefaultPatientSerializer):
    doctor = serializers.PrimaryKeyRelatedField(read_only=True)
    doctor_name = serializers.SerializerMethodField()

    class Meta(DefaultPatientSerializer.Meta):
        fields = DefaultPatientSerializer.Meta.fields + ['doctor_name']


class PatientSignUpSerializer(UserCreateMixin, PatientSerializer):
    user = BaseUserSignUpSerializer()
    doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())


class PatientRetrieveSerializer(PatientSerializer):
    class Meta(PatientSerializer.Meta):
        fields = PatientSerializer.Meta.fields
        read_only_fields = ['first_name', 'last_name', 'age']


class AccountsTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user: 'BaseUser'):
        token = CustomRefreshToken.for_user(user)
        return token


class AccountsTokenRefreshSerializer(RefreshBlacklistMixin, TokenRefreshSerializer):
    @transaction.atomic
    def validate(self, attrs: dict):
        refresh_obj = CustomRefreshToken(attrs['refresh'])
        data = {'access': str(refresh_obj.access_token)}
        access_token_exp = refresh_obj.access_token.payload['exp']

        self.try_blacklist(refresh=refresh_obj)
        self.set_refresh_payload(refresh=refresh_obj)
        self.set_user_expired_to(epoch_time=access_token_exp)

        refresh_token = str(refresh_obj)
        data['refresh'] = refresh_token

        return data


# serializer relation은 core app에서 처리할 예정
class SimpleRelatedDoctorSerializer(DoctorListSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())


class SimpleRelatedPatientSerializer(PatientListSerailizer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())


class RelatedDoctorSerializer(DoctorListSerializer):
    pass


class RelatedPatientSerializer(PatientListSerailizer):
    doctor = DoctorListSerializer()
