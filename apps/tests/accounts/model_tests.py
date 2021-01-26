# import pytest
#
# from accounts.models import BaseUser, BaseQuerySet, Doctor
#
# """Doctor"""
#
#
# @pytest.mark.django_db
# def test_create_doctor(doctor_with_group):
#     doctors = Doctor.objects.all()
#     assert doctors.count() == 1
#     assert doctor_with_group == doctors.first()
#
#
# def test_create_doctors(doctors_with_group):
#     assert doctors_with_group
#     assert doctors_with_group.count() == 5
#
#
# @pytest.mark.django_db
# def test_doctor_get_absolute_url(doctor_with_group):
#     assert doctor_with_group.get_absolute_url() == '/accounts/doctors/' + str(doctor_with_group.user_id)
#
#
# @pytest.mark.django_db
# def test_check_is_doctor(doctor_with_group):
#     assert doctor_with_group.user.is_patient is False
#     assert doctor_with_group.user.is_doctor is True
#
#
# """Patient"""
#
#
# @pytest.mark.django_db
# def test_create_patient(patient_with_group):
#     assert patient_with_group.user.email == 'patient@test.com'
#     assert patient_with_group.user.groups.filter(name='patient').exists()
#
#
# @pytest.mark.django_db
# def test_create_patients(patients_with_group):
#     assert patients_with_group.count() == 5
#
#
# @pytest.mark.django_db
# def test_patient_get_absolute_url(patient_with_group):
#     assert patient_with_group.get_absolute_url() == '/accounts/patients/' + str(patient_with_group.pk)
#
#
# @pytest.mark.django_db
# def test_check_is_patient(patient_with_group):
#     assert patient_with_group.user.is_patient is True
#     assert patient_with_group.user.is_doctor is False
#
#
# """BaseUser"""
#
#
# @pytest.mark.django_db
# def test_create_baseuser(baseuser):
#     assert baseuser.email == 'test@test.com'
#
#
# @pytest.mark.django_db
# def test_baseuser_method_str(baseuser):
#     assert str(baseuser) == baseuser.email
#
#
# @pytest.mark.django_db
# def test_baseuser_queryset_active(create_bundle_user_with_some_inactive):
#     users = BaseUser.objects.all()
#     # is_active == False
#     inactive = users.filter(is_active=False)
#     assert inactive.count() == 5
#     # is_active == True
#     active = users.active()
#     assert active.count() == 5
#     for user in active:
#         assert user.is_active
#
#
# @pytest.mark.django_db
# def test_baseuser_method_is_doctor_or_patient(baseuser):
#     assert baseuser.is_doctor is False
#     assert baseuser.is_patient is False
#
#
# @pytest.mark.django_db
# def test_child_account_from_baseuser(doctor_with_group, patient_with_group):
#     assert doctor_with_group.user.get_child_account() == doctor_with_group
#     assert patient_with_group.user.get_child_account() == patient_with_group
#
#
# """SuperUser"""
#
#
# @pytest.mark.django_db
# def test_queryset(baseuser):
#     users = BaseUser.objects.all()
#     assert isinstance(users, BaseQuerySet)
