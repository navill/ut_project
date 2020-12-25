import pytest
from rest_framework.reverse import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'user, department, major, status_code', [
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
)
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


@pytest.mark.django_db
@pytest.mark.parametrize(
    'user, age, emergency_call, status_code', [
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
)
def test_api_signup_patient_with_parameters(api_client, create_doctor_with_group, user, age, emergency_call,
                                            status_code):
    baseuser, doctor = create_doctor_with_group
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


@pytest.mark.django_db
def test_api_create_token_by_login(api_client, create_doctor_with_group):
    user, doctor = create_doctor_with_group
    url = reverse('token-login')
    response = api_client.post(url, data={'username': user.username, 'password': 'test12345'}, format='json')

    # success
    assert user.username == 'doctortest'
    assert response.status_code == 200
    assert 'access' in response.data
    assert 'refresh' in response.data

    # fail - invalid user info
    response = api_client.post(url, data={'username': user.username, 'password': 'test00000'}, format='json')
    assert response.status_code == 401
    response = api_client.post(url, data={'username': 'unknownuser', 'password': 'test12345'}, format='json')
    assert response.status_code == 401


@pytest.mark.django_db
def test_api_access_doctors_with_token(api_client, get_access_and_refresh_token_from_doctor):
    refresh, access = get_access_and_refresh_token_from_doctor
    url = reverse('accounts:doctor-list')
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access)
    response = api_client.get(url, format='json')

    # success
    assert response.status_code == 200
    assert url in response.data[0]['url']
    assert response.data[0]['user']['username'] == 'doctortest'
    assert response.data[0]['department'] == 'chosun'
    assert response.data[0]['major'] == 'Psychiatrist'

    # fail - no authentication
    api_client.credentials()
    response = api_client.get(url, format='json')
    assert response.status_code == 401


# todo: test_api_access_patient_with_token() + crudl 관련 테스트 생성
