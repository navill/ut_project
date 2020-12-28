import pytest
from rest_framework.reverse import reverse

from accounts.tests.conftest import DOCTOR_PARAMETER, PATIENT_PARAMETER

api_accounts_parameter_test_condition = False
api_test_condition = False


@pytest.mark.skipif(api_accounts_parameter_test_condition, reason='passed')
@pytest.mark.django_db
@pytest.mark.parametrize(*DOCTOR_PARAMETER)
def test_api_signup_doctor_with_parameters(api_client, user, department, major, status_code):
    data = {
        'user': user,
        'department': department,
        'major': major
    }
    url = reverse('accounts:api-signup-doctor')
    response = api_client.post(url, data=data, format='json')

    assert response.status_code == status_code
    if response.status_code == 201:
        assert response.data['user']['username'] == 'doctortest'


@pytest.mark.skipif(api_accounts_parameter_test_condition, reason='passed')
@pytest.mark.django_db
@pytest.mark.parametrize(*PATIENT_PARAMETER)
def test_api_signup_patient_with_parameters(api_client, user_doctor_with_group, user, age, emergency_call,
                                            status_code):
    baseuser, doctor = user_doctor_with_group
    data = {
        'user_doctor': doctor.pk,
        'user': user,
        'age': age,
        'emergency_call': emergency_call
    }
    url = reverse('accounts:api-signup-patient')
    response = api_client.post(url, data=data, format='json')

    assert response.status_code == status_code
    if response.status_code == 201:
        assert response.data['user']['username'] == 'patienttest'


@pytest.mark.skipif(api_test_condition, reason='passed')
@pytest.mark.django_db
def test_api_create_token_by_login_with_doctor_info(api_client, user_doctor_with_group):
    user, doctor = user_doctor_with_group
    url = reverse('token-login')
    response = api_client.post(url, data={'username': user.username, 'password': 'test12345'}, format='json')

    # success
    assert user.username == 'doctortest'
    assert response.status_code == 200
    assert 'access' in response.data
    assert 'refresh' in response.data

    # fail - 유효하지 않은 인증 정보
    response = api_client.post(url, data={'username': user.username, 'password': 'test00000'}, format='json')
    assert response.status_code == 401
    response = api_client.post(url, data={'username': 'unknownuser', 'password': 'test12345'}, format='json')
    assert response.status_code == 401


@pytest.mark.skipif(api_test_condition, reason='passed')
@pytest.mark.django_db
def test_api_create_token_by_login_with_patient_info(api_client, user_patient_with_group):
    user, patient = user_patient_with_group
    url = reverse('token-login')
    response = api_client.post(url, data={'username': user.username, 'password': 'test12345'}, format='json')

    # success
    assert user.username == 'patienttest'
    assert response.status_code == 200

    # fail - 유효하지 않은 인증 정보
    response = api_client.post(url, data={'username': user.username, 'password': 'test00000'}, format='json')
    assert response.status_code == 401
    response = api_client.post(url, data={'username': 'unknownuser', 'password': 'test12345'}, format='json')
    assert response.status_code == 401


@pytest.mark.skipif(api_test_condition, reason='passed')
@pytest.mark.django_db
def test_api_view_doctor_list_with_doctor_token(api_client, get_access_and_refresh_token_from_doctor):
    # create doctor & token
    refresh, access = get_access_and_refresh_token_from_doctor
    url = reverse('accounts:doctor-list')
    # authenticate token
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access)
    response = api_client.get(url, format='json')

    # list - success
    assert response.status_code == 200
    assert url in response.data[0]['url']
    assert response.data[0]['user']['username'] == 'doctortest'
    assert response.data[0]['department'] == 'chosun'
    assert response.data[0]['major'] == 'Psychiatrist'

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
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access)
    response = api_client.get(url, format='json')

    # success
    assert response.status_code == 200
    assert url in response.data[0]['url']
    assert response.data[0]['user']['username'] == 'patienttest'
    assert response.data[0]['age'] == 30
    assert response.data[0]['emergency_call'] == '062-119'

    # fail - 인증 x
    api_client.credentials()
    response = api_client.get(url, format='json')
    assert response.status_code == 401


@pytest.mark.skipif(api_test_condition, reason='passed')
@pytest.mark.django_db
def test_api_view_doctor_detail(api_client, get_access_and_refresh_token_from_doctor):
    refresh, access = get_access_and_refresh_token_from_doctor
    # authenticate token
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access)

    # detail - success
    url = reverse('accounts:doctor-detail-update', kwargs={'pk': 1})
    response = api_client.get(url, format='json')
    assert response.status_code == 200
    assert response.data['user']['username'] == 'doctortest'

    # fail - 인증 x
    api_client.credentials()
    response = api_client.get(url, format='json')
    assert response.status_code == 401


@pytest.mark.skipif(api_test_condition, reason='passed')
@pytest.mark.django_db
def test_api_update_doctor(api_client, get_access_and_refresh_token_from_doctor):
    refresh, access = get_access_and_refresh_token_from_doctor
    # authenticate token
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access)
    url = reverse('accounts:doctor-detail-update', kwargs={'pk': 1})

    # update - success(입력 없음 - 변경 x)
    response = api_client.put(url, format='json')
    assert response.data['department'] == 'chosun'
    assert response.data['major'] == 'Psychiatrist'

    # update - success(데이터 변경)
    data = {
        'department': 'changed department',
    }
    response = api_client.put(url, data=data, format='json')
    assert response.status_code == 200
    assert response.data['department'] == 'changed department'
    assert response.data['major'] != 'changed major'

    # fail - 인증 x
    api_client.credentials()
    response = api_client.get(url, format='json')
    assert response.status_code == 401
