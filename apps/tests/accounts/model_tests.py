import datetime

import pytest
from django.contrib.auth.models import Group
from django.utils.timezone import now

from accounts.models import *
from hospitals.models import Major
from tests.constants import *


@pytest.mark.django_db
def test_baseuser():
    baseuser = User.objects.select_all().first()
    assert baseuser


@pytest.mark.django_db
def test_create_baseuser():
    user = User.objects.create_user(email='test@test.com', password='test1234')
    assert user
    new_user = User.objects.last()
    assert new_user.email == 'test@test.com'
    assert new_user.is_active
    assert not new_user.is_staff
    assert not new_user.is_superuser


@pytest.mark.django_db
def test_create_superuser():
    superuser = User.objects.create_superuser(email='superuser@superuser.com', password='test1234')
    assert superuser.is_active
    assert superuser.is_staff
    assert superuser.is_superuser


@pytest.mark.django_db
def test_create_doctor():
    user = User.objects.create_user(email='testdoctor@doctor.com', password='test1234')
    major = Major.objects.first()
    doctor = Doctor.objects.create(user=user, major=major, **DOCTOR)
    assert doctor.user.email == 'testdoctor@doctor.com'
    assert not user.user_type


@pytest.mark.django_db
def test_doctor_queryset(django_assert_num_queries):
    doctor = Doctor.objects.first()
    with django_assert_num_queries(3) as captured1:
        print(doctor.patients.all())  # query 1
        print(doctor.patients.all())  # query 2
        print(doctor.major.id)  # query 3
        # print(doctor.patient_user_id)

    select_all_doctor = Doctor.objects.select_all().first()  # with major
    with django_assert_num_queries(2) as captured2:
        print(select_all_doctor.patients.all())  # query 1
        print(select_all_doctor.patients.all())  # query 2
        print(select_all_doctor.major.id)
        # print(select_all_doctor.patient_user_id)

    doctor_with_patients = Doctor.objects.select_all().prefetch_all().first()  # with major, patients
    with django_assert_num_queries(0) as captured3:
        print(doctor_with_patients.patients.all())
        print(doctor_with_patients.patients.all())
        print(doctor_with_patients.major.id)


@pytest.mark.django_db
def test_create_patient():
    user = User.objects.create_user(email='testpatient@patient.com', password='test1234')
    doctor = Doctor.objects.first()
    patient = Patient.objects.create(user=user, doctor=doctor, **PATIENT)
    assert patient.user.email == 'testpatient@patient.com'
    assert patient.doctor.user_id == doctor.user_id
    assert not hasattr(patient, 'age')
    # manager->queryset이 실행되어야 age 호출 가능
    patient = Patient.objects.get(user_id=user.id)
    assert patient.age


@pytest.mark.django_db
def test_patient_age_by_birth():
    patient = Patient.objects.first()
    patient.birth = datetime.date(1988, 12, 31)
    patient.save()

    # 오늘 날짜를 기준으로 생일이 지나지 않은 유저
    patient = Patient.objects.first()
    assert patient.age == 32

    # 오늘 날짜를 기준으로 생일이 지난 유저
    now_date = now().date()
    patient.birth = datetime.date(1988, now_date.month, now_date.day)
    patient.save()
    patient = Patient.objects.first()
    assert patient.age == 33


@pytest.mark.django_db
def test_patient_queryset(django_assert_num_queries):
    patient = Patient.objects.all().first()
    print(Patient.objects.all().explain())
    with django_assert_num_queries(3) as captured1:
        print(patient.prescriptions.all())  # query 1
        print(patient.doctor.first_name)  # query 2
        print(patient.user.email)  # query 3

    patient = Patient.objects.select_all().first()  # with doctor
    with django_assert_num_queries(3) as captured2:
        print(patient.prescriptions.all())  # query 1
        print(patient.prescriptions.all())  # query 2
        print(patient.doctor.first_name)  # query 3
        print(patient.user.email)

    patient = Patient.objects.select_all().prefetch_all().first()  # with doctor, prescriptions
    with django_assert_num_queries(1) as captured3:
        print(patient.doctor.first_name)  # query 1
        print(patient.user.email)
        print(patient.prescriptions.all())
        print(patient.prescriptions.all())


@pytest.mark.django_db
def test_check_user_type():
    baseuser = BaseUser.objects.first()
    assert not baseuser.user_type

    group = Group.objects.get(name='doctor')
    baseuser.set_user_type(group.name)
    assert baseuser.user_type
    assert baseuser.user_type.doctor
    assert not baseuser.user_type.patient
