import pytest

from accounts.models import BaseUser, BaseQuerySet
from tests.conftest import USER_BASEUSER

doctor_test_condition = False
patient_test_condition = False
baseuser_test_condition = False
superuser_test_condition = False
# doctor_test_condition = True
# patient_test_condition = True
# baseuser_test_condition = True
# superuser_test_condition = True


"""Doctor"""


@pytest.mark.skipif(doctor_test_condition, reason='passed')
def test_create_doctor(user_doctor_with_group):
    user, doctor = user_doctor_with_group
    assert user.email == 'doctor@test.com'
    assert user.groups.filter(name='doctor').exists()
    assert user.pk == 1
    assert doctor.get_full_name() == 'firstdoctor lastdoctor'
    assert doctor.pk == 1
    assert doctor.major.name == '정신의학'


@pytest.mark.skipif(doctor_test_condition, reason='passed')
def test_doctor_get_absolute_url(user_doctor_with_group):
    user, doctor = user_doctor_with_group
    assert doctor.get_absolute_url() == '/accounts/doctors/' + str(doctor.pk)


@pytest.mark.skipif(doctor_test_condition, reason='passed')
def test_check_is_doctor(user_doctor_with_group):
    user, doctor = user_doctor_with_group
    assert user.is_patient is False
    assert user.is_doctor is True


"""Patient"""


@pytest.mark.skipif(patient_test_condition, reason='passed')
def test_create_patient(user_patient_with_group):
    user, patient = user_patient_with_group
    assert user.email == 'patient@test.com'
    assert user.groups.filter(name='patient').exists()
    assert patient.pk == 2
    assert patient.doctor.pk == 1


@pytest.mark.skipif(patient_test_condition, reason='passed')
def test_patient_get_absolute_url(user_patient_with_group):
    user, patient = user_patient_with_group
    assert patient.get_absolute_url() == '/accounts/patients/' + str(patient.pk)


@pytest.mark.skipif(patient_test_condition, reason='passed')
def test_check_is_patient(user_patient_with_group):
    user, patient = user_patient_with_group
    assert user.is_patient is True
    assert user.is_doctor is False


"""BaseUser"""


@pytest.mark.skipif(baseuser_test_condition, reason='passed')
@pytest.mark.django_db
def test_create_baseuser(baseuser):
    user = baseuser
    assert user.email == 'test@test.com'


@pytest.mark.skipif(baseuser_test_condition, reason='passed')
@pytest.mark.django_db
def test_baseuser_method_str(baseuser):
    user = baseuser
    assert str(user) == user.email


@pytest.mark.skipif(baseuser_test_condition, reason='passed')
@pytest.mark.django_db
def test_baseuser_queryset_active(create_bundle_user_with_some_inactive):
    users = BaseUser.objects.all()
    # with is_active == False
    for user in users:
        if user.id % 2 != 0:
            assert user.is_active is False
    # only is_active == True
    active_user = users.active()
    for user in active_user:
        assert user.is_active


@pytest.mark.skipif(baseuser_test_condition, reason='passed')
@pytest.mark.django_db
def test_baseuser_method_is_doctor_or_patient(baseuser):
    user = baseuser
    assert user.is_doctor is False
    assert user.is_patient is False


"""SuperUser"""


@pytest.mark.skipif(superuser_test_condition, reason='passed')
@pytest.mark.django_db
def test_create_superuser(super_user):
    super_user = super_user
    assert super_user.is_superuser
    assert super_user.is_staff
    assert super_user.is_active

    with pytest.raises(ValueError):
        USER_BASEUSER['email'] = 'no_staff_superuser'
        BaseUser.objects.create_superuser(**USER_BASEUSER, is_staff=False)
    with pytest.raises(ValueError):
        USER_BASEUSER['email'] = 'no_supersuer_superuser'
        BaseUser.objects.create_superuser(**USER_BASEUSER, is_superuser=False)


@pytest.mark.skipif(superuser_test_condition, reason='passed')
@pytest.mark.django_db
def test_queryset(baseuser):
    users = BaseUser.objects.all()
    assert isinstance(users, BaseQuerySet)
