from django.db import transaction
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings

from accounts.api.authentications import CustomRefreshToken
from accounts.api.mixins import UserCreateMixin
from accounts.models import BaseUser, Doctor, Patient


class BaseUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(read_only=True)
    date_joined = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", read_only=True)
    date_updated = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", read_only=True)
    last_login = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", read_only=True)

    class Meta:
        model = BaseUser
        fields = ['username', 'first_name', 'last_name', 'date_joined', 'date_updated', 'last_login']


class BaseUserSignUpSerializer(BaseUserSerializer):
    username = serializers.CharField(validators=[UniqueValidator(queryset=BaseUser.objects.all())])
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password', 'placeholder': 'Password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password', 'placeholder': 'Confirm Password'}
    )

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + ['password', 'password2']

    def validate(self, data):
        # if not data.get('password') or not data.get('password2'):
        #     raise serializers.ValidationError("Please enter passwords.")
        if data.get('password') != data.get('password2'):
            raise serializers.ValidationError("Those passwords do not match.")
        data.pop('password2')
        return data


class DoctorSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='accounts:doctor-detail-update',
        lookup_field='pk',
        read_only=True
    )
    user = BaseUserSerializer(read_only=True)

    class Meta:
        model = Doctor
        fields = ['url', 'user', 'department', 'major']


class PatientSerailizer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='accounts:patient-detail-update',
        lookup_field='pk',
        read_only=True
    )
    user = BaseUserSerializer(read_only=True)

    class Meta:
        model = Patient
        fields = ['url', 'user_doctor', 'user', 'age', 'emergency_call']
        read_only_fields = ['user_doctor', 'user']  # 의사를 수정할 일이 있는가?


class DoctorSignUpSerializer(UserCreateMixin, DoctorSerializer):
    user = BaseUserSignUpSerializer()


class PatientSignUpSerializer(UserCreateMixin, PatientSerailizer):
    user = BaseUserSignUpSerializer()
    user_doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())


# serializer relation은 core app에서 처리할 예정
class SimpleRelatedDoctorSerializer(DoctorSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=BaseUser.objects.all())


class SimpleRelatedPatientSerializer(PatientSerailizer):
    user = serializers.PrimaryKeyRelatedField(queryset=BaseUser.objects.all())
    user_doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())


class RelatedDoctorSerializer(DoctorSerializer):
    pass


class RelatedPatientSerializer(PatientSerailizer):
    user_doctor = DoctorSerializer()


class AccountsTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = CustomRefreshToken.for_user(user)
        return token


class AccountsTokenRefreshSerializer(TokenRefreshSerializer):
    @transaction.atomic
    def validate(self, attrs):
        refresh = CustomRefreshToken(attrs['refresh'])
        data = {'access': str(refresh.access_token)}
        exp = refresh.access_token.payload['exp']

        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    # create() Blacklist
                    refresh.blacklist()

                except AttributeError:
                    pass

            refresh.set_jti()
            refresh.set_exp()  # from_time = self.current
            data['refresh'] = str(refresh)

            # save() user.token_expired()
            self._set_user_expired_to(exp=exp)
        return data

    def _set_user_expired_to(self, exp: int = None):  # exp: epoch time
        user = self.context['request'].user
        user.set_token_expired(exp)
