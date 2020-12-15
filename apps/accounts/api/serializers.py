from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from accounts.api.mixins import UserCreateMixin
from accounts.models import BaseUser, Doctor, Patient


class BaseUserSignUpSerializer(serializers.ModelSerializer):
    username = serializers.CharField(validators=[UniqueValidator(queryset=BaseUser.objects.all())])
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password', 'placeholder': 'Password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password', 'placeholder': 'Password'}
    )
    date_joined = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", read_only=True)
    date_updated = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", read_only=True)
    last_login = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", read_only=True)

    class Meta:
        model = BaseUser
        fields = ['username', 'password', 'password2', 'date_joined', 'date_updated', 'last_login']


class BaseDoctorSerializer(serializers.ModelSerializer):
    user = BaseUserSignUpSerializer()

    class Meta:
        model = Doctor
        fields = ['user', 'department', 'major']


class DoctorSignUpSerializer(UserCreateMixin, BaseDoctorSerializer):
    pass


class BasePatientSerailizer(serializers.ModelSerializer):
    user = BaseUserSignUpSerializer()
    family_doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())

    class Meta:
        model = Patient
        fields = ['family_doctor', 'user', 'age', 'emergency_call']


class PatientSignUpSerializer(UserCreateMixin, BasePatientSerailizer):
    pass
