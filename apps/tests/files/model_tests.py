# from uuid import UUID
#
# import pytest
#
# from files.models import DataFile
#
#
# @pytest.mark.django_db
# def test_created_file_instance(data_file_by_doctor):
#     assert isinstance(data_file_by_doctor.id, UUID)
#     assert data_file_by_doctor.uploader.email == 'doctor@test.com'
#     assert data_file_by_doctor.checked is True
#     assert data_file_by_doctor.status == "NORMAL"
#     assert data_file_by_doctor.file == '/Users/jh/Desktop/ut_django/apps/storage/test_file.md'
#
#
# @pytest.mark.django_db
# def test_model_is_uploader(data_file_by_doctor, doctor_with_group, patient_with_group):
#     assert data_file_by_doctor.is_uploader(doctor_with_group.user)
#     assert data_file_by_doctor.is_uploader(patient_with_group.user) is False
#
#
# @pytest.mark.django_db
# def test_model_queryset_unchecked_file_list(data_file_bundle_by_doctor):
#     queryset = DataFile.objects.all()
#     assert queryset.count() == 5
#     assert queryset.filter_unchecked_list().count() == 0
#
#     datafile_obj = queryset.first()
#     datafile_obj.checked = False
#     datafile_obj.save()
#     assert queryset.filter_unchecked_list().count() == 1
#
#
# @pytest.mark.django_db
# def test_model_queryset_filter_current_user(doctor_with_group, data_file_by_doctor):
#     queryset = DataFile.objects.all()
#     assert queryset.filter_uploader(doctor_with_group.user)
#
#
# @pytest.mark.django_db
# def test_model_manager_owner_queryset(doctor_with_group, super_user, data_file_by_doctor):
#     queryset = DataFile.objects.owner_queryset(user=doctor_with_group.user)
#     assert queryset.count()
#     queryset = DataFile.objects.owner_queryset(user=super_user)
#     assert queryset.count()
