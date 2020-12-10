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
    date_joined = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", read_only=True)
    date_updated = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", read_only=True)
    last_login = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", read_only=True)

    class Meta:
        model = BaseUser
        fields = ['username', 'password', 'password2', 'date_joined', 'date_updated', 'last_login']


class DoctorSerializer(serializers.ModelSerializer):
    user = BaseUserSignUpSerializer()

    class Meta:
        model = Doctor
        fields = '__all__'


class DoctorSignUpSerializer(BaseUserSignUpSerializer):
    user = BaseUserSignUpSerializer()

    class Meta:
        model = Doctor
        fields = ['user', 'department', 'major']


class PatientSignUpSerializer(BaseUserSignUpSerializer):
    user = BaseUserSignUpSerializer()
    doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())
    emergency_call = serializers.CharField(max_length=14)

    class Meta:
        model = Patient
        fields = ['doctor', 'user', 'age', 'emergency_call']


class PatientSerializer(serializers.ModelSerializer):
    created = serializers.SerializerMethodField()
    updated = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = '__all__'

    def get_created(self, obj):
        return obj.user.date_joined

    def get_updated(self, obj):
        return obj.user.date_updated
