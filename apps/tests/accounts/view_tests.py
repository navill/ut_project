import pytest
from rest_framework.reverse import reverse

from accounts.api.authentications import CustomRefreshToken
from accounts.models import Doctor, Patient
from tests.conftest import DOCTOR_PARAMETER, PATIENT_PARAMETER


@pytest.mark.parametrize(*DOCTOR_PARAMETER)
@pytest.mark.django_db
def test_api_create_signup_doctor_with_parameters(api_client, major, user, first_name, last_name,
                                                  address, phone, description, status_code):
    data = {
        'user': user,
        'first_name': first_name,
        'last_name': last_name,
        'address': address,
        'phone': phone,
        'description': description,
        'major': major.id,
        'gender': 'MALE'
    }
    assert major.id
    url = reverse('accounts:api-signup-doctor')
    response = api_client.post(url, data=data, format='json')
    assert response.status_code == status_code
    if response.status_code == 201:
        assert response.data['user']['email'] == 'doctor@test.com'


@pytest.mark.parametrize(*PATIENT_PARAMETER)
@pytest.mark.django_db
def test_api_create_signup_patient_with_parameters(api_client, doctor_with_group, user, first_name, last_name,
                                                   address, phone, birth, emergency_call, status_code):
    doctor = doctor_with_group
    data = {
        'doctor': doctor.user_id,
        'user': user,
        'first_name': first_name,
        'last_name': last_name,
        'address': address,
        'phone': phone,
        'birth': birth,
        'emergency_call': emergency_call,
        'gender': 'MALE'
    }
    url = reverse('accounts:api-signup-patient')
    response = api_client.post(url, data=data, format='json')

    assert response.status_code == status_code
    if response.status_code == 201:
        assert response.data['user']['email'] == 'patient@test.com'


def test_api_create_token_by_login_with_doctor_info(api_client, doctor_with_group):
    url = reverse('token-login')
    response = api_client.post(url, data={'email': doctor_with_group.user.email, 'password': 'test12345'},
                               format='json')
    doctor = doctor_with_group
    # success
    assert doctor_with_group.user.email == 'doctor@test.com'
    assert response.status_code == 200
    assert 'access' in response.data
    assert 'refresh' in response.data
    assert response.data['main_url'] == reverse('core-api:doctors:detail', kwargs={'pk': doctor.user_id})

    # fail - 유효하지 않은 인증 정보
    response = api_client.post(
        url, data={'email': doctor.user.email, 'password': 'invalidpasswd'}, format='json'
    )
    assert response.status_code == 401
    response = api_client.post(
        url, data={'email': 'unknownuser', 'password': 'test12345'}, format='json'
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_api_create_token_by_login_with_patient_info(api_client, patient_with_group):
    patient = patient_with_group
    url = reverse('token-login')
    response = api_client.post(url, data={'email': patient.user.email, 'password': 'test12345'}, format='json')

    # success
    assert patient.user.email == 'patient@test.com'
    assert response.status_code == 200
    assert response.data['main_url'] == reverse('core-api:patients:main', kwargs={'pk': patient.user_id})

    # fail - 유효하지 않은 인증 정보
    response = api_client.post(url, data={'email': patient.user.email, 'password': 'test00000'}, format='json')
    assert response.status_code == 401
    response = api_client.post(url, data={'email': 'unknownuser', 'password': 'test12345'}, format='json')
    assert response.status_code == 401


def test_api_view_doctor_list_with_doctor_token(api_client, get_access_and_refresh_token_from_doctor):
    # create doctor & token
    refresh, access = get_access_and_refresh_token_from_doctor
    url = reverse('accounts:doctor-list')
    # authenticate token
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(access))
    response = api_client.get(url, format='json')

    # list - success
    assert response.status_code == 200
    assert url in response.data['results'][0]['url']
    # fail - 유효하지 않은 인증 정보
    api_client.credentials()
    response = api_client.get(url, format='json')
    assert response.status_code == 403


def test_api_view_patient_list_with_doctor_token(api_client, get_access_and_refresh_token_from_doctor,
                                                 patient_with_group):
    refresh, access = get_access_and_refresh_token_from_doctor
    url = reverse('accounts:patient-list')
    # authenticate token
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(access))
    response = api_client.get(url, format='json')

    # success
    assert response.status_code == 200
    assert url in response.data['results'][0]['url']

    # fail - 인증 x
    api_client.credentials()
    response = api_client.get(url, format='json')
    assert response.status_code == 403


@pytest.mark.django_db
def test_api_retrieve_doctor(api_client):
    doctor = Doctor.objects.first()
    token = CustomRefreshToken.for_user(doctor.user)

    # authenticate token
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token.access_token))
    doctor = Doctor.objects.get(user_id=2)
    # detail - success
    url = reverse('accounts:doctor-detail', kwargs={'pk': doctor.user_id})
    response = api_client.get(url, format='json')
    assert response.status_code == 200
    # fail - 인증 x
    api_client.credentials()
    response = api_client.get(url, format='json')
    assert response.status_code == 403  # 401: 익명, 403: 로그인은 했지만 권한이 없음


@pytest.mark.django_db
def test_api_update_doctor(api_client):
    doctor = Doctor.objects.first()
    token = CustomRefreshToken.for_user(doctor.user)
    # 토큰 인증
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token.access_token))
    url = reverse('accounts:doctor-update', kwargs={'pk': doctor.user_id})
    # 데이터 변경(PUT)
    data = {'description': 'changed description'}
    response = api_client.put(url, data=data, format='json')
    assert response.status_code == 200
    assert response.data['description'] == 'changed description'
