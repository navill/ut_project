from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer

from accounts.api.authentications import CustomRefreshToken
from accounts.api.mixins import UserCreateMixin, RefreshBlacklistMixin
from accounts.models import Doctor, Patient, Gender
from hospitals.api.serializers import DefaultMajorSerializer
from hospitals.models import Major

if TYPE_CHECKING:
    from accounts.models import BaseUser

User = get_user_model()


class RawAccountSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    gender = serializers.CharField(read_only=True)
    address = serializers.CharField()
    phone = serializers.CharField()
    full_name = serializers.SerializerMethodField()

    def get_full_name(self, instance):
        return instance.full_name


# BaseUser

class DefaultBaseUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email']


class BaseUserSerializer(DefaultBaseUserSerializer):
    class Meta(DefaultBaseUserSerializer.Meta):
        fields = DefaultBaseUserSerializer.Meta.fields


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

    def validate(self, data: dict):
        self._check_matched_password(data)
        return data

    def _check_matched_password(self, data: dict):
        if data.get('password') != data.get('password2'):
            raise serializers.ValidationError("Those passwords do not match.")
        data.pop('password2')


# Doctor
class RawDoctorSerializer(RawAccountSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='accounts:doctor-detail-update',
        lookup_field='pk',
        read_only=True
    )

    class Meta:
        model = Doctor
        fields = ['url', 'user_id', 'full_name', 'gender']


class RelatedDoctorSerializer(RawDoctorSerializer):
    user = DefaultBaseUserSerializer(read_only=True)
    major = DefaultMajorSerializer(read_only=True)

    class Meta(RawDoctorSerializer.Meta):
        fields = RawDoctorSerializer.Meta.fields + ['user', 'major']

    def get_user_email(self, instance):
        return instance.user.email

    def get_major_name(self, instance):
        return instance.major.name


class DoctorSerializer(RelatedDoctorSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    major = serializers.PrimaryKeyRelatedField(read_only=True)
    user_email = serializers.SerializerMethodField()
    major_name = serializers.SerializerMethodField()

    class Meta(RelatedDoctorSerializer.Meta):
        fields = RelatedDoctorSerializer.Meta.fields + ['user_email', 'major_name', 'address', 'phone', 'description']


class DoctorListSerializer(RawDoctorSerializer):
    major_name = serializers.SerializerMethodField()

    class Meta(RawDoctorSerializer.Meta):
        fields = RawDoctorSerializer.Meta.fields + ['major_name']

    def get_major_name(self, instance):
        return instance.major.name


class DoctorRetrieveSerializer(RawDoctorSerializer):
    class Meta(RawDoctorSerializer.Meta):
        fields = RawDoctorSerializer.Meta.fields + ['address', 'phone', 'description']


class DoctorSignUpSerializer(UserCreateMixin, DoctorSerializer):
    user = BaseUserSignUpSerializer()
    major = serializers.PrimaryKeyRelatedField(queryset=Major.objects.all())
    gender = serializers.ChoiceField(choices=Gender.choices)
    first_name = serializers.CharField()
    last_name = serializers.CharField()

    class Meta(DoctorSerializer.Meta):
        # fields = DoctorSerializer.Meta.fields + ['first_name', 'last_name']
        fields = ['url', 'user', 'first_name', 'last_name', 'address', 'phone', 'description', 'major']


# Patient

class RawPatientSerializer(RawAccountSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='accounts:patient-detail-update',
        lookup_field='pk',
        read_only=True
    )

    class Meta:
        model = Patient
        fields = ['url', 'user_id', 'full_name', 'gender']


class RelatedPatientSerializer(RawPatientSerializer):
    user = DefaultBaseUserSerializer()
    doctor = RelatedDoctorSerializer()

    class Meta(RawPatientSerializer.Meta):
        fields = RawPatientSerializer.Meta.fields + ['user', 'doctor']

    def get_user_email(self, instance):
        return instance.user.email

    def get_doctor_name(self, instance):
        return instance.doctor.get_full_name()


class PatientSerializer(RelatedPatientSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    doctor = serializers.PrimaryKeyRelatedField(read_only=True)
    user_email = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()

    class Meta(RelatedPatientSerializer.Meta):
        fields = RelatedPatientSerializer.Meta.fields + \
                 ['user_email', 'doctor_name', 'address', 'phone', 'age', 'emergency_call']


class PatientListSerailizer(RawPatientSerializer):
    class Meta(RawPatientSerializer.Meta):
        fields = RawPatientSerializer.Meta.fields + ['age']


class PatientSignUpSerializer(UserCreateMixin, PatientSerializer):
    user = BaseUserSignUpSerializer()
    doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())
    gender = serializers.ChoiceField(choices=Gender.choices)


class PatientRetrieveSerializer(RawPatientSerializer):
    class Meta(RawPatientSerializer.Meta):
        fields = RawPatientSerializer.Meta.fields + ['phone', 'address', 'emergency_call']


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
