import uuid

import pytest
from django.contrib.auth.models import Group

from accounts.api.authentications import CustomRefreshToken
from accounts.models import Doctor, Patient
from files.models import DataFile
from hospitals.models import Major, Department, MedicalCenter
from prescriptions.models import Prescription
from tests.constants import USER_BASEUSER, User, USER_DOCTOR, DOCTOR, USER_PATIENT, PATIENT, DATAFILE


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
    instance = User.objects.create_superuser(**USER_BASEUSER)
    return instance


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
    instances = User.objects.bulk_create(user_values)
    return instances


@pytest.fixture
def baseuser():
    instance = User.objects.create_user(**USER_BASEUSER)
    return instance


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
    instance = MedicalCenter.objects.create(**data)
    return instance


@pytest.fixture
def department(hospital):
    data = {
        'medical_center': hospital,
        'name': '정신의학과',
        'call': '062-333-3333'
    }
    instance = Department.objects.create(**data)
    return instance


@pytest.fixture
def major(department):
    data = {
        'department': department,
        'name': '정신의학',
        'call': '062-444-4444'
    }
    instance = Major.objects.create(**data)
    return instance


@pytest.fixture
def prescription(db, user_doctor_with_group, user_patient_with_group):
    doctor_baseuser, doctor = user_doctor_with_group
    patient_baseuser, patient = user_patient_with_group
    data = {
        'writer': doctor,
        'user_patient': patient,
        'description': 'test 처방'
    }
    instance = Prescription.objects.create(**data)
    return instance


@pytest.fixture
def generated_uuid4():
    return uuid.uuid4()


@pytest.fixture
def data_file_by_doctor(db, generated_uuid4, prescription, user_doctor_with_group):
    DATAFILE['id'] = generated_uuid4
    DATAFILE['prescription'] = prescription
    DATAFILE['uploader'] = user_doctor_with_group[0]
    instance = DataFile.objects.create(**DATAFILE)
    return instance


@pytest.fixture
def data_file_unchecked(data_file_by_doctor):
    data_file_by_doctor.status = False
    data_file_by_doctor.save()
    return data_file_by_doctor
