import pytest

# 210208

# doctor
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.reverse import reverse

from accounts.api.authentications import CustomRefreshToken
from accounts.models import Doctor, Patient
from config.settings.local import MEDIA_ROOT
from files.models import DoctorFile
from prescriptions.models import HealthStatus, Prescription


@pytest.mark.django_db
def test_core_api_doctor_profile_detail_for_doctor(api_client):
    doctor = Doctor.objects.first()
    refresh = CustomRefreshToken.for_user(doctor.user)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(refresh.access_token))
    url = reverse('core-api:doctors:doctor-profile', kwargs={'pk': doctor.user_id})
    response = api_client.get(url)

    assert response.status_code == 200

    other_doctor = Doctor.objects.last()
    refresh = CustomRefreshToken.for_user(other_doctor.user)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(refresh.access_token))
    url = reverse('core-api:doctors:doctor-profile', kwargs={'pk': doctor.user_id})
    response_fail = api_client.get(url)

    assert response_fail.status_code == 403


@pytest.mark.django_db
def test_core_api_doctor_profile_update_for_doctor(api_client, get_token_with_doctor):
    data = {'phone': '010-987-654', 'description': 'updated description'}
    doctor, refresh = get_token_with_doctor
    old_phone, old_description = doctor.phone, doctor.description

    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(refresh.access_token))
    url = reverse('core-api:doctors:doctor-profile', kwargs={'pk': doctor.user_id})
    response = api_client.patch(url, data=data)

    assert response.status_code == 200
    assert response.data['phone'] != old_phone
    assert response.data['description'] != old_description

    other_doctor = Doctor.objects.last()
    refresh = CustomRefreshToken.for_user(other_doctor.user)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(refresh.access_token))
    url = reverse('core-api:doctors:doctor-profile', kwargs={'pk': doctor.user_id})
    response = api_client.patch(url, data={'phone': '010-987-654', 'description': 'updated description'})

    assert response.status_code == 403


# patient fields: user_id, first_name, last_name, gender, phone, address, emergency_call
@pytest.mark.django_db
def test_core_api_patient_profile_detail_for_doctor(api_client, get_token_with_doctor):
    doctor, refresh = get_token_with_doctor
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(refresh.access_token))

    patients = Patient.objects.filter(doctor_id=doctor.user_id)
    for patient_id in patients.values_list('user_id', flat=True):
        url = reverse('core-api:doctors:patient-profile', kwargs={'pk': patient_id})
        response = api_client.get(url)
        assert response.status_code == 200

    not_care_patients = Patient.objects.exclude(doctor_id=doctor.user_id)
    for patient_id in not_care_patients.values_list('user_id', flat=True):
        url = reverse('core-api:doctors:patient-profile', kwargs={'pk': patient_id})
        response = api_client.get(url)
        assert response.status_code == 403


@pytest.mark.django_db
def test_core_api_patient_profile_update_for_doctor(api_client, get_token_with_doctor):
    data = {'data': 'can not send data to patient profile'}
    doctor, refresh = get_token_with_doctor
    patient = Patient.objects.filter(doctor_id=doctor.user_id).first()
    not_care_patient = Patient.objects.exclude(doctor_id=doctor.user_id).first()

    for patient in (patient, not_care_patient):
        url = reverse('core-api:doctors:patient-profile', kwargs={'pk': patient.user_id})
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(refresh.access_token))
        response = api_client.patch(url, data=data)
        assert response.status_code == 405


@pytest.mark.django_db
def test_core_api_prescription_create(api_client, get_token_with_doctor, data_file_bundle_by_doctor):
    doctor, refresh = get_token_with_doctor
    patient = Patient.objects.filter(doctor_id=doctor.user_id).first()
    upload_file_list = (SimpleUploadedFile(f"testfile{number}.txt", b"test file", content_type='multipart/form-data')
                        for number in range(3))

    data = {
        'patient': patient.user_id,
        'description': 'test prescription',
        'doctor_upload_files': upload_file_list,
        'status': HealthStatus.UNKNOWN,
        'checked': False,
        'start_date': '2021-02-01',
        'end_date': '2021-02-10',
    }

    url = reverse('core-api:doctors:prescription-create')
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(refresh.access_token))
    response = api_client.post(url, data=data)

    assert response.status_code == 201
    assert len(response.data['doctor_files']) == 3

    # 생성된 prescription & doctorfile 확인
    created_prescription = Prescription.objects.first()
    doctor_files = DoctorFile.objects.filter(prescription_id=created_prescription.id)

    assert created_prescription.description == 'test prescription'
    assert doctor_files.count() == 3


@pytest.mark.django_db
def test_core_api_prescription_detail_update(api_client, get_token_with_doctor):
    doctor, refresh = get_token_with_doctor
    prescription = Prescription.objects.first()
    data = {'description': 'updated prescription'}

    url = reverse('core-api:doctors:prescription-detail', kwargs={'pk': prescription.id})
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(refresh.access_token))
    response = api_client.patch(url, data=data)

    assert response.status_code == 200
    assert response.data['description'] != prescription.description


@pytest.mark.django_db
def test_core_api_file_prescription_detail_update():
    pass


@pytest.mark.django_db
def test_core_api_doctor_file_create():
    pass


@pytest.mark.django_db
def test_core_api_doctor_file_detail_update():
    pass
