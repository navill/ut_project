from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from accounts.api.mixins import UserCreateMixin
from accounts.models import BaseUser, Doctor, Patient


class IdRelatedSerializer(serializers.Serializer):
    user = serializers.IntegerField()


class BaseUserSerializer(serializers.ModelSerializer):
    date_joined = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", read_only=True)
    date_updated = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", read_only=True)
    last_login = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", read_only=True)

    class Meta:
        model = BaseUser
        fields = ['username', 'date_joined', 'date_updated', 'last_login']


class UserSignUpSerializer(BaseUserSerializer):
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

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + ['password', 'password2', ]


class DoctorSerializer(serializers.ModelSerializer):
    user = BaseUserSerializer()

    class Meta:
        model = Doctor
        fields = ['user', 'department', 'major']


class SimpleRelatedDoctorSerializer(DoctorSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=BaseUser.objects.all())


class DoctorSignUpSerializer(UserCreateMixin, DoctorSerializer):
    pass


class PatientSerailizer(serializers.ModelSerializer):
    user = BaseUserSerializer()
    user_doctor = SimpleRelatedDoctorSerializer()

    class Meta:
        model = Patient
        fields = ['user', 'user_doctor', 'age', 'emergency_call']


class SimpleRelatedPatientSerializer(PatientSerailizer):
    user = serializers.PrimaryKeyRelatedField(queryset=BaseUser.objects.all())
    user_doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())


class PatientSignUpSerializer(UserCreateMixin, PatientSerailizer):
    pass
