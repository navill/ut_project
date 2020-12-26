import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from accounts.api.authentications import CustomRefreshToken
from accounts.models import Doctor, Patient


class Skip:
    def __init__(self):
        self._is_skip = False

    @property
    def is_skip(self):
        return self._is_skip

    @is_skip.setter
    def is_skip(self, bool_value):
        self._is_skip = bool_value


class ParameterizeTestCondition(Skip):
    pass


class APITestCondition(Skip):
    pass


# User = get_user_model()
USER_DOCTOR = {
    'username': 'doctortest',
    'first_name': 'doctor',
    'last_name': 'lastname',
    'password': 'test12345'
}

USER_PATIENT = {
    'username': 'patienttest',
    'first_name': 'patient',
    'last_name': 'lastname',
    'password': 'test12345'
}

DOCTOR_ACCOUNT = {
    'department': 'chosun',
    'major': 'Psychiatrist'
}

PATIENT_ACCOUNT = {
    'age': 30,
    'emergency_call': '062-119'
}

User = get_user_model()


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def get_access_and_refresh_token_from_doctor(create_doctor_with_group):
    user, doctor = create_doctor_with_group
    token = CustomRefreshToken.for_user(user)
    return str(token), str(token.access_token)


@pytest.fixture
def create_doctor_with_group(db):
    user = User.objects.create_user(**USER_DOCTOR)
    doctor = Doctor.objects.create(user=user, **DOCTOR_ACCOUNT)
    group = Group.objects.create(name='doctor')
    user.groups.add(group)
    return user, doctor


@pytest.fixture
def create_patient_with_group(db, create_doctor_with_group):
    user_doctor, doctor = create_doctor_with_group
    user = User.objects.create_user(**USER_PATIENT)
    patient = Patient.objects.create(user=user, user_doctor=doctor, **PATIENT_ACCOUNT)
    group = Group.objects.create(name='patient')
    user.groups.add(group)
    return user, patient
