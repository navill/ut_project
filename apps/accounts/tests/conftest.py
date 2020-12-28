import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from accounts.api.authentications import CustomRefreshToken
from accounts.models import Doctor, Patient


class Skip:
    check = False
    skip = True


class ParameterizeTestCondition(Skip):
    pass


class APITestCondition(Skip):
    pass


class ModelTestCondition(Skip):
    pass


DOCTOR_PARAMETER = 'user, department, major, status_code', [
    ({
         'username': 'doctortest',  # 201
         'first_name': 'doctor',
         'last_name': 'lastname',
         'password': 'test12345',
         'password2': 'test12345',
     }, 'chosun', 'Psychiatrist', 201),
    ({
         'username': 'doctortest',  # not match password
         'first_name': 'doctor',
         'last_name': 'lastname',
         'password': 'test12345',
         'password2': 'test54321',
     }, 'chosun', 'Psychiatrist', 400),
    ({
         'username': 'doctortest',  # no password2
         'first_name': 'doctor',
         'last_name': 'lastname',
         'password': 'test12345',
         'password2': '',
     }, 'chosun', 'Psychiatrist', 400),
    ({
         'username': 'doctortest',  # no password
         'first_name': 'doctor',
         'last_name': 'lastname',
         'password': '',
         'password2': 'test12345',
     }, 'chosun', 'Psychiatrist', 400),
    ({
         'username': 'doctortest',  # no department
         'first_name': 'doctor',
         'last_name': 'lastname',
         'password': 'test12345',
         'password2': 'test12345',
     }, '', 'Psychiatrist', 400),
    ({
         'username': 'doctortest',  # no major
         'first_name': 'doctor',
         'last_name': 'lastname',
         'password': 'test12345',
         'password2': 'test12345',
     }, 'chosun', '', 400),
]
PATIENT_PARAMETER = 'user, age, emergency_call, status_code', [
    ({
         'username': 'patienttest',  # 201
         'first_name': 'patient',
         'last_name': 'lastname',
         'password': 'test12345',
         'password2': 'test12345',
     }, 30, '010-119', 201),
    ({
         'username': 'patienttest',  # not match password
         'first_name': 'patient',
         'last_name': 'lastname',
         'password': 'test12345',
         'password2': 'test54321',
     }, 30, '010-119', 400),
    ({
         'username': 'patienttest',  # no password2
         'first_name': 'patient',
         'last_name': 'lastname',
         'password': 'test12345',
         'password2': '',
     }, 30, '010-119', 400),
    ({
         'username': 'patienttest',  # no password
         'first_name': 'patient',
         'last_name': 'lastname',
         'password': '',
         'password2': 'test12345',
     }, 30, '010-119', 400),
    ({
         'username': 'patienttest',  # no age
         'first_name': 'patient',
         'last_name': 'lastname',
         'password': 'test12345',
         'password2': 'test12345',
     }, '', '010-119', 400),
    ({
         'username': 'patienttest',  # no emergency_call
         'first_name': 'patient',
         'last_name': 'lastname',
         'password': 'test12345',
         'password2': 'test12345',
     }, 30, '', 400),
]
# User = get_user_model()

USER_BASEUSER = {
    'username': 'baseuser',
    'first_name': 'base',
    'last_name': 'user',
    'password': 'test12345'
}

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
def create_super_user():
    super_user = User.objects.create_superuser(**USER_BASEUSER)
    return super_user


@pytest.fixture
def create_bundle_users_with_some_inactive():
    user_values = []
    for i in range(10):
        value = {
            'username': f'baseuser{i}',
            'first_name': f'base{i}',
            'last_name': f'user{i}',
            'password': 'test12345'
        }
        if i % 2 == 0:
            value['is_active'] = False
        user_values.append(User(**value))
    users = User.objects.bulk_create(user_values)
    return users


@pytest.fixture
def create_baseuser():
    user = User.objects.create_user(**USER_BASEUSER)
    return user


@pytest.fixture
def get_access_and_refresh_token_from_doctor(user_doctor_with_group):
    user, doctor = user_doctor_with_group
    token = CustomRefreshToken.for_user(user)
    return str(token), str(token.access_token)


@pytest.fixture
def user_doctor_with_group(db):
    user = User.objects.create_user(**USER_DOCTOR)
    doctor = Doctor.objects.create(user=user, **DOCTOR_ACCOUNT)
    group = Group.objects.create(name='doctor')
    user.groups.add(group)
    return user, doctor


@pytest.fixture
def user_patient_with_group(db, user_doctor_with_group):
    user_doctor, doctor = user_doctor_with_group
    user = User.objects.create_user(**USER_PATIENT)
    patient = Patient.objects.create(user=user, user_doctor=doctor, **PATIENT_ACCOUNT)
    group = Group.objects.create(name='patient')
    user.groups.add(group)
    return user, patient
