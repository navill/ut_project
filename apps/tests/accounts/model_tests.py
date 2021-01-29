import pytest

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
    assert not new_user.is_doctor
    assert not new_user.is_patient


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
    assert doctor.user.is_doctor


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
