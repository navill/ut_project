import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.reverse import reverse

from accounts.api.authentications import CustomRefreshToken
from accounts.models import Doctor, Patient

# User = get_user_model()
USER_DOCTOR = {
    'username': 'doctortest',
    'first_name': 'firstname',
    'last_name': 'lastname',
    'password': 'test12345'
}

USER_PATIENT = {
    'username': 'patienttest',
    'first_name': 'firstname',
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
def get_access_refresh_token(create_doctor):
    user, doctor = create_doctor
    token = CustomRefreshToken.for_user(user)
    return str(token), str(token.access_token)


@pytest.fixture
def create_doctor(db):
    user = User.objects.create(**USER_DOCTOR)
    doctor = Doctor.objects.create(user=user, **DOCTOR_ACCOUNT)
    group = Group.objects.create(name='doctor')
    user.groups.add(group)
    return user, doctor


@pytest.fixture
def create_patient(db, create_doctor):
    user_doctor, doctor = create_doctor
    user = User.objects.create(**USER_PATIENT)
    patient = Patient.objects.create(user=user, user_doctor=doctor, **PATIENT_ACCOUNT)
    group = Group.objects.create(name='patient')
    user.groups.add(group)
    return user, patient


def test_doctor(create_doctor):
    user, doctor = create_doctor
    assert user.username == 'doctortest'
    assert user.groups.filter(name='doctor').exists()
    assert doctor.pk == 1
    assert user.pk == 1


def test_create_patient(create_patient):
    user, patient = create_patient
    assert user.username == 'patienttest'
    assert user.groups.filter(name='patient').exists()
    assert patient.user_doctor.pk == 1


#
@pytest.mark.django_db
def test_signup_doctor(api_client):
    doctor_data = {
        'user': {
            'username': 'doctortest',
            'first_name': 'firstname',
            'last_name': 'lastname',
            'password': 'test12345',
            'password2': 'test12345',
        },
        'department': 'chosun',
        'major': 'Psychiatrist'
    }
    url = reverse('accounts:api-signup-doctor')
    response = api_client.post(url, data=doctor_data, format='json')
    assert response.status_code == 201


@pytest.mark.django_db
def test_signup_patient(api_client, create_doctor):
    user, doctor = create_doctor
    patient_data = {
        'user_doctor': doctor.user_id,
        'user': {
            'username': 'patienttest',
            'first_name': 'firstname',
            'last_name': 'lastname',
            'password': 'test12345',
            'password2': 'test12345',
        },
        'age': 30,
        'emergency_call': '119'
    }
    url = reverse('accounts:api-signup-patient')
    response = api_client.post(url, data=patient_data, format='json')
    assert response.status_code == 201


@pytest.mark.django_db
def test_get_access_refresh_token_from_doctor(api_client, get_access_refresh_token):
    refresh, access = get_access_refresh_token
    url = reverse('accounts:doctor-list')
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access)
    response = api_client.get(url, format='json')
    assert get_access_refresh_token
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_access_refresh_token_from_url(api_client, get_access_refresh_token, create_doctor):
    user, doctor = create_doctor
    refresh, access = get_access_refresh_token
    response = api_client.login(username=user.username, password=user.password)
