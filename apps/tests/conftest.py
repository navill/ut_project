import os
import uuid

import pytest
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from rest_framework.reverse import reverse

from accounts.api.authentications import CustomRefreshToken
from accounts.models import Doctor, Patient
from config.settings.base import BASE_DIR
from files.models import DoctorFile, PatientFile
from hospitals.models import Major, Department, MedicalCenter
from prescriptions.models import Prescription
from tests.constants import *


@pytest.fixture(scope='session')
def django_db_setup():
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '127.0.0.1',
        'NAME': 'project_test',
    }


@pytest.fixture(scope='function')
def doctor_with_group(major):
    user = User.objects.create_user(**USER_DOCTOR)
    doctor = Doctor.objects.create(user_id=user.id, major=major, **DOCTOR)
    group, created = Group.objects.get_or_create(name='doctor')
    user.groups.add(group)
    return doctor


@pytest.fixture(scope='function')
def doctors_with_group(major):
    group, created = Group.objects.get_or_create(name='doctor')

    for i in range(5):
        user = User.objects.create_user(email=f'doctor{i}@test.com', password='test1234')
        user.groups.add(group)
        Doctor.objects.create(user_id=user.id,
                              first_name=f'의사{i}',
                              last_name=f'성{i}',
                              address='광주어딘가..',
                              phone=f'010-111-11{i}',
                              description=f'test{i}',
                              major=major)

    return Doctor.objects.all()


@pytest.fixture(scope='function')
def patient_with_group(doctor_with_group):
    user = User.objects.create_user(**USER_PATIENT)
    patient = Patient.objects.create(user_id=user.id, doctor=doctor_with_group, **PATIENT)
    group, created = Group.objects.get_or_create(name='patient')
    user.groups.add(group)
    return patient


@pytest.fixture(scope='function')
def patients_with_group(doctor_with_group):
    group, created = Group.objects.get_or_create(name='patient')

    for i in range(5):
        user = User.objects.create_user(email=f'patient{i}@test.com', password='test1234')
        user.groups.add(group)

        Patient.objects.create(user_id=user.id,
                               doctor=doctor_with_group,
                               first_name=f'환자{i}',
                               last_name=f'성{i}',
                               address='광주 어디',
                               phone=f'010-2222-22{i}',
                               age=30 + i,
                               emergency_call=f'010-333-333{i}'
                               )
    return Patient.objects.all()


@pytest.fixture(scope='function')
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture(scope='function')
def super_user():
    instance = User.objects.create_superuser(**USER_BASEUSER)
    return instance


@pytest.fixture(scope='function')
def create_bundle_user_with_some_inactive():
    for i in range(10):
        value = {
            'email': f'test{i}@test.com',
            'password': 'test12345'
        }
        if i % 2 == 0:
            value['is_active'] = False
        User.objects.create_user(**value)
    # instances = User.objects.bulk_create(user_values)
    return User.objects.all()


@pytest.fixture(scope='function')
def baseuser():
    instance = User.objects.create_user(**USER_BASEUSER)
    return instance


@pytest.fixture(scope='function')
def get_access_and_refresh_token_from_doctor(doctor_with_group):
    token = CustomRefreshToken.for_user(doctor_with_group.user)
    return str(token), str(token.access_token)


@pytest.fixture(scope='function')
def get_token_from_doctor(doctor_with_group):
    return CustomRefreshToken.for_user(doctor_with_group.user)


@pytest.fixture(scope='function')
def get_token_from_patient(patient_with_group):
    return CustomRefreshToken.for_user(patient_with_group.user)


@pytest.fixture(scope='function')
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


@pytest.fixture(scope='function')
def department(hospital):
    data = {
        'medical_center': hospital,
        'name': '정신의학과',
        'call': '062-333-3333'
    }
    instance = Department.objects.create(**data)
    return instance


@pytest.fixture(scope='function')
def major(department):
    data = {
        'department': department,
        'name': '정신의학',
        'call': '062-444-4444'
    }
    instance = Major.objects.create(**data)
    return instance


@pytest.fixture(scope='function')
def prescription(doctor_with_group, patient_with_group):
    data = {
        'writer': doctor_with_group,
        'patient': patient_with_group,
        'description': 'test 처방'
    }
    instance = Prescription.objects.create(**data)
    return instance


@pytest.fixture(scope='function')
def bundle_prescriptions(doctor_with_group, patient_with_group):
    bulk_data = []
    for i in range(5):
        bulk_data.append(
            Prescription(
                writer=doctor_with_group,
                patient=patient_with_group,
                prescription='처방-' + str(i)
            )
        )
    Prescription.objects.bulk_create(bulk_data)


@pytest.fixture(scope='function')
def generated_uuid4():
    return uuid.uuid4()


def renew_uuid():
    return uuid.uuid4()


@pytest.fixture(scope='function')
def data_file_unchecked(data_file_by_doctor):
    data_file_by_doctor.checked = False
    data_file_by_doctor.save()
    return data_file_by_doctor


@pytest.fixture(scope='function')
def doctor_client_with_token_auth(api_client, get_token_from_doctor):
    access = get_token_from_doctor.access_token
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(access))
    return api_client


@pytest.fixture(scope='function')
def patient_client_with_token_auth(api_client, get_token_from_patient):
    access = get_token_from_patient.access_token
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(access))
    return api_client


@pytest.fixture(scope='function')
def get_token_with_doctor():
    doctor = Doctor.objects.first()
    refresh = CustomRefreshToken.for_user(doctor.user)
    return doctor, refresh


@pytest.fixture(scope='function')
def get_token_with_patient():
    patient = Patient.objects.first()
    refresh = CustomRefreshToken.for_user(patient.user)
    return patient, refresh


@pytest.fixture(scope='function')
def data_file_bundle_by_doctor(prescription):
    # bulk_data = []
    doctor = Doctor.objects.first()
    uploader_id = doctor.user_id
    prescription_id = prescription.id
    file = MEDIA_ROOT + '/test_file.md'
    datafile = {
        'id': None,
        'prescription_id': prescription.id,
        'uploader_id': doctor.user_id,
        'file': MEDIA_ROOT + '/test_file.md',
    }
    for _ in range(5):
        datafile['id'] = renew_uuid()
        # bulk_data.append(DataFile(**datafile))
        DoctorFile.objects.create(uploader_id=uploader_id, prescription_id=prescription_id, file=file)
    # DataFile.objects.bulk_create(bulk_data)
    return DoctorFile.objects.filter(uploader_id=uploader_id)


@pytest.fixture(scope='function')
def doctor_file_bundle():
    upload_file_list = (SimpleUploadedFile(f"testfile{number}.txt", b"test file", content_type='multipart/form-data')
                        for number in range(3))
    yield upload_file_list

# @pytest.fixture(scope='function')
# def data_file_bundle_by_patient(prescription, patient_with_group):
#     # bulk_data = []
#     datafile = {
#         'id': None,
#         'prescription': prescription,
#         'uploader': patient_with_group.user,
#         'file': MEDIA_ROOT + '/test_file.md',
#         'checked': False,
#         'status': HealthStatus.NORMAL
#     }
#     for _ in range(5):
#         datafile['id'] = renew_uuid()
#         # bulk_data.append(DataFile(**datafile))
#         PatientFile.objects.create(**datafile)
#         # DataFile.objects.bulk_create(bulk_data)
#     return PatientFile.objects.filter(uploader=patient_with_group.user)
