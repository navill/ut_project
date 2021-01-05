from uuid import UUID

import pytest

from files.models import DataFile


@pytest.mark.django_db
def test_created_file_instance(data_file_by_doctor):
    assert isinstance(data_file_by_doctor.id, UUID)
    assert data_file_by_doctor.uploader.email == 'doctor@test.com'
    assert data_file_by_doctor.checked is True
    assert data_file_by_doctor.status == "NORMAL"
    assert data_file_by_doctor.file == '/Users/jh/Desktop/ut_django/apps/storage/test_file.md'


@pytest.mark.django_db
def test_model_is_uploader(data_file_by_doctor, user_doctor_with_group, user_patient_with_group):
    doctor_user, doctor = user_doctor_with_group
    patient_user, patient = user_patient_with_group
    assert data_file_by_doctor.is_uploader(doctor_user)
    assert data_file_by_doctor.is_uploader(patient_user) is False


@pytest.mark.django_db
def test_model_queryset_unchecked_file_list(data_file_unchecked):
    queryset = DataFile.objects.all()
    assert queryset.unchecked_list().count() == 0


@pytest.mark.django_db
def test_model_queryset_filter_current_user(user_doctor_with_group, data_file_by_doctor):
    queryset = DataFile.objects.all()
    user, doctor = user_doctor_with_group
    assert queryset.filter_current_user(user)


@pytest.mark.django_db
def test_model_manager_owner_queryset(user_doctor_with_group, super_user, data_file_by_doctor):
    user, doctor = user_doctor_with_group
    queryset = DataFile.objects.owner_queryset(user)
    assert queryset.count()
    queryset = DataFile.objects.owner_queryset(super_user)
    assert queryset.count()
