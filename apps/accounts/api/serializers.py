from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from accounts.api.mixins import UserCreateMixin
from accounts.models import BaseUser, Doctor, Patient


class BaseUserSignUpSerializer(UserCreateMixin, serializers.ModelSerializer):
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

    class Meta:
        model = BaseUser
        fields = ['username', 'password', 'password2']


class DoctorSignUpSerializer(BaseUserSignUpSerializer):
    user = BaseUserSignUpSerializer()

    class Meta:
        model = Doctor
        fields = ['user', 'department', 'major']


class DoctorListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'


class PatientSignUpSerializer(BaseUserSignUpSerializer):
    user = BaseUserSignUpSerializer()
    doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())
    emergency_call = serializers.CharField(max_length=14)

    class Meta:
        model = Patient
        fields = ['doctor', 'user', 'age', 'emergency_call']


class PatientListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'
