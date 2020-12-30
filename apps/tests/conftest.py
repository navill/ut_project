import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from accounts.api.authentications import CustomRefreshToken
from accounts.models import Doctor, Patient

from hospitals.models import Major, Department, MedicalCenter

DOCTOR_PARAMETER = 'user, first_name, last_name, address, phone, description, status_code', [
    ({
         'email': 'doctor@test.com',  # 201
         'password': 'test12345',
         'password2': 'test12345',
     }, 'first_doctor', 'last_doctor', '광주어딘가..', '010-111-1111', '의사입니다.', 201),
    ({
         'email': 'doctor@test.com',  # not match password
         'first_name': 'doctor',
         'last_name': 'lastname',
         'password': 'test12345',
         'password2': 'test54321',
     }, 'first_doctor', 'last_doctor', '광주어딘가..', '010-111-1111', '의사입니다.', 400),
    ({
         'email': 'doctor@test.com',  # no password2
         'first_name': 'doctor',
         'last_name': 'lastname',
         'password': 'test12345',
         'password2': '',
     }, 'first_doctor', 'last_doctor', '광주어딘가..', '010-111-1111', '의사입니다.', 400),
    ({
         'email': 'doctor@test.com',  # no password
         'first_name': 'doctor',
         'last_name': 'lastname',
         'password': '',
         'password2': 'test12345',
     }, 'first_doctor', 'last_doctor', '광주어딘가..', '010-111-1111', '의사입니다.', 400),

]
PATIENT_PARAMETER = 'user, first_name, last_name, address, phone, age, emergency_call, status_code', [
    ({
         'email': 'patient@test.com',  # 201
         'password': 'test12345',
         'password2': 'test12345',
     }, '길동', '홍', '광주 어딘가', '010-1111-1111', 30, '010-119', 201),
    ({
         'email': 'patient@test.com',  # not match password
         'first_name': 'patient',
         'last_name': 'lastname',
         'password': 'test12345',
         'password2': 'test54321',
     }, '길동', '홍', '광주 어딘가', '010-1111-1111', 30, '010-119', 400),
    ({
         'email': 'patient@test.com',  # no password2
         'first_name': 'patient',
         'last_name': 'lastname',
         'password': 'test12345',
         'password2': '',
     }, '길동', '홍', '광주 어딘가', '010-1111-1111', 30, '010-119', 400),
    ({
         'email': 'patient@test.com',  # no password
         'first_name': 'patient',
         'last_name': 'lastname',
         'password': '',
         'password2': 'test12345',
     }, '길동', '홍', '광주 어딘가', '010-1111-1111', 30, '010-119', 400),
    ({
         'email': 'patient@test.com',  # no age
         'first_name': 'patient',
         'last_name': 'lastname',
         'password': 'test12345',
         'password2': 'test12345',
     }, '길동', '홍', '광주 어딘가','010-1111-1111', '', '010-119', 400),
    ({
         'email': 'patient@test.com',  # no emergency_call
         'first_name': 'patient',
         'last_name': 'lastname',
         'password': 'test12345',
         'password2': 'test12345',
     }, '길동', '홍', '광주 어딘가', '010-1111-1111', 30, '', 400),
]

USER_BASEUSER = {
    'email': 'test@test.com',
    'password': 'test12345'
}
USER_PATIENT = {
    'email': 'patient@test.com',
    'password': 'test12345'
}

USER_DOCTOR = {
    'email': 'doctor@test.com',
    'password': 'test12345'
}
DOCTOR = {
    'first_name': 'firstdoctor',
    'last_name': 'lastdoctor',
    'address': '광주광역시 어디어디..',
    'phone': '010-111-1111',
    'description': '의사입니다.'
}

# USER_PATIENT = {
#     'email': 'patient@test.com',
#     'password': 'test1234'
# }
PATIENT = {
    'first_name': 'firstpatient',
    'last_name': 'lastpatient',
    'address': '광주광역시 어디어디..',
    'phone': '010-3333-3333',
    'age': 30,
    'emergency_call': '010-119'
}

User = get_user_model()


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


#
# @pytest.fixture
# def create_medicalcenter():
#     data = {
#         'country': '한국',
#         'city': '서울특별시',
#         'name': '한국병원',
#         'address': '강남구...',
#         'postal_code': '123-123',
#         'main_call': '02-111-2222',
#         'sub_call': '02-222-3333'
#     }
#     mc = MedicalCenter.objects.create(**data)
#     return mc
#
#
# @pytest.fixture
# def create_department(create_medicalcenter):
#     data = {
#         'medical_center': create_medicalcenter,
#         'name': '정신의학과',
#         'call': '02-333-4444'
#     }
#     department = Department.objects.create(**data)
#     return department


@pytest.fixture
def super_user():
    super_user = User.objects.create_superuser(**USER_BASEUSER)
    return super_user


@pytest.fixture
def create_bundle_user_with_some_inactive():
    user_values = []
    for i in range(10):
        value = {
            'email': f'test{i}@test.com',
            'password': 'test12345'
        }
        if i % 2 == 0:
            value['is_active'] = False
        user_values.append(User(**value))
    users = User.objects.bulk_create(user_values)
    return users


@pytest.fixture
def baseuser():
    user = User.objects.create_user(**USER_BASEUSER)
    return user


@pytest.fixture
def get_access_and_refresh_token_from_doctor(user_doctor_with_group):
    user, doctor = user_doctor_with_group
    token = CustomRefreshToken.for_user(user)
    return str(token), str(token.access_token)


@pytest.fixture
def get_token_from_doctor(user_doctor_with_group):
    user, _ = user_doctor_with_group
    return CustomRefreshToken.for_user(user)


@pytest.fixture
def user_doctor_with_group(db, major):
    user = User.objects.create_user(**USER_DOCTOR)
    doctor = Doctor.objects.create(user=user, major=major, **DOCTOR)
    group = Group.objects.create(name='doctor')
    user.groups.add(group)
    return user, doctor


@pytest.fixture
def user_patient_with_group(db, user_doctor_with_group):
    user_doctor, doctor = user_doctor_with_group
    user = User.objects.create_user(**USER_PATIENT)
    patient = Patient.objects.create(user=user, doctor=doctor, **PATIENT)
    group = Group.objects.create(name='patient')
    user.groups.add(group)
    return user, patient


@pytest.fixture
def hospital(db):
    data = {
        'country': '대한민국',
        'city': '광주',
        'name': '한국병원',
        'address': '광주 광역시 ...',
        'postal_code': '12345',
        'main_call': '062-111-1111',
        'sub_call': '062-222-2222'
    }
    medical_object = MedicalCenter.objects.create(**data)
    return medical_object


@pytest.fixture
def department(hospital):
    data = {
        'medical_center': hospital,
        'name': '정신의학과',
        'call': '062-333-3333'
    }
    department_object = Department.objects.create(**data)
    return department_object


@pytest.fixture
def major(department):
    data = {
        'department': department,
        'name': '정신의학',
        'call': '062-444-4444'
    }
    major_object = Major.objects.create(**data)
    return major_object
