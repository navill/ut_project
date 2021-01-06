import pytest
from rest_framework.reverse import reverse

from tests.conftest import DOCTOR_PARAMETER, PATIENT_PARAMETER

api_accounts_parameter_test_condition = False
api_test_condition = False


@pytest.mark.skipif(api_accounts_parameter_test_condition, reason='passed')
@pytest.mark.django_db
@pytest.mark.parametrize(*DOCTOR_PARAMETER)
def test_api_create_signup_doctor_with_parameters(api_client, major, user, first_name, last_name, address, phone,
                                                  description,
                                                  status_code):
    assert major.id
    data = {
        'user': user,
        'firs_name': first_name,
        'last_name': last_name,
        'address': address,
        'phone': phone,
        'description': description,
        'major': major.id
    }
    url = reverse('accounts:api-signup-doctor')
    response = api_client.post(url, data=data, format='json')

    assert response.status_code == status_code
    if response.status_code == 201:
        assert response.data['user']['email'] == 'doctor@test.com'


@pytest.mark.skipif(api_accounts_parameter_test_condition, reason='passed')
@pytest.mark.django_db
@pytest.mark.parametrize(*PATIENT_PARAMETER)
def test_api_create_signup_patient_with_parameters(api_client, user_doctor_with_group, user, first_name, last_name,
                                                   address, phone, age, emergency_call, status_code):
    baseuser, doctor = user_doctor_with_group
    data = {
        'doctor': doctor.pk,
        'user': user,
        'first_name': first_name,
        'last_name': last_name,
        'address': address,
        'phone': phone,
        'age': age,
        'emergency_call': emergency_call
    }
    url = reverse('accounts:api-signup-patient')
    response = api_client.post(url, data=data, format='json')

    assert response.status_code == status_code
    if response.status_code == 201:
        assert response.data['user']['email'] == 'patient@test.com'


@pytest.mark.skipif(api_test_condition, reason='passed')
@pytest.mark.django_db
def test_api_create_token_by_login_with_doctor_info(api_client, user_doctor_with_group):
    user, doctor = user_doctor_with_group
    url = reverse('token-login')
    response = api_client.post(url, data={'email': user.email, 'password': 'test12345'}, format='json')

    # success
    assert user.email == 'doctor@test.com'
    assert response.status_code == 200
    assert 'access' in response.data
    assert 'refresh' in response.data

    # fail - 유효하지 않은 인증 정보
    response = api_client.post(url, data={'email': user.email, 'password': 'test00000'}, format='json')
    assert response.status_code == 401
    response = api_client.post(url, data={'email': 'unknownuser', 'password': 'test12345'}, format='json')
    assert response.status_code == 401


@pytest.mark.skipif(api_test_condition, reason='passed')
@pytest.mark.django_db
def test_api_create_token_by_login_with_patient_info(api_client, user_patient_with_group):
    user, patient = user_patient_with_group
    url = reverse('token-login')
    response = api_client.post(url, data={'email': user.email, 'password': 'test12345'}, format='json')

    # success
    assert user.email == 'patient@test.com'
    assert response.status_code == 200

    # fail - 유효하지 않은 인증 정보
    response = api_client.post(url, data={'email': user.email, 'password': 'test00000'}, format='json')
    assert response.status_code == 401
    response = api_client.post(url, data={'email': 'unknownuser', 'password': 'test12345'}, format='json')
    assert response.status_code == 401


@pytest.mark.skipif(api_test_condition, reason='passed')
@pytest.mark.django_db
def test_api_view_doctor_list_with_doctor_token(api_client, get_access_and_refresh_token_from_doctor):
    # create doctor & token
    refresh, access = get_access_and_refresh_token_from_doctor
    url = reverse('accounts:doctor-list')
    # authenticate token
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(access))
    response = api_client.get(url, format='json')

    # list - success
    assert response.status_code == 200
    assert url in response.data[0]['url']
    assert response.data[0]['user']['email'] == 'doctor@test.com'

    # fail - 유효하지 않은 인증 정보
    api_client.credentials()
    response = api_client.get(url, format='json')
    assert response.status_code == 401


@pytest.mark.skipif(api_test_condition, reason='passed')
@pytest.mark.django_db
def test_api_view_patient_list_with_doctor_token(api_client, get_access_and_refresh_token_from_doctor,
                                                 user_patient_with_group):
    # create patient
    _, _ = user_patient_with_group
    # create doctor & token
    refresh, access = get_access_and_refresh_token_from_doctor
    url = reverse('accounts:patient-list')
    # authenticate token
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(access))
    response = api_client.get(url, format='json')

    # success
    assert response.status_code == 200
    assert url in response.data[0]['url']
    assert response.data[0]['user']['email'] == 'patient@test.com'
    assert response.data[0]['age'] == 30
    assert response.data[0]['emergency_call'] == '010-119'

    # fail - 인증 x
    api_client.credentials()
    response = api_client.get(url, format='json')
    assert response.status_code == 401


@pytest.mark.skipif(api_test_condition, reason='passed')
@pytest.mark.django_db
def test_api_retrieve_doctor(api_client, get_access_and_refresh_token_from_doctor):
    refresh, access = get_access_and_refresh_token_from_doctor
    # authenticate token
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(access))

    # detail - success
    url = reverse('accounts:doctor-detail-update', kwargs={'pk': 1})
    response = api_client.get(url, format='json')
    assert response.status_code == 200
    assert response.data['user']['email'] == 'doctor@test.com'

    # fail - 인증 x
    api_client.credentials()
    response = api_client.get(url, format='json')
    assert response.status_code == 401


@pytest.mark.skipif(api_test_condition, reason='passed')
@pytest.mark.django_db
def test_api_update_doctor(api_client, get_access_and_refresh_token_from_doctor):
    refresh, access = get_access_and_refresh_token_from_doctor

    # 토큰 인증
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(access))
    url = reverse('accounts:doctor-detail-update', kwargs={'pk': 1})
    response = api_client.get(url, format='json')
    assert response.status_code == 200

    # 데이터 변경(PATCH)
    data = {'description': 'changed description'}
    response = api_client.patch(url, data=data, format='json')
    assert response.status_code == 200
    assert response.data['description'] == 'changed description'
