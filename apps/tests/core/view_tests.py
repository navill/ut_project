import pytest

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.reverse import reverse

from accounts.api.authentications import CustomRefreshToken
from accounts.models import Doctor, Patient
from files.models import DoctorFile
from prescriptions.models import HealthStatus, Prescription, FilePrescription


@pytest.mark.django_db
def test_core_api_doctor_profile_detail_for_doctor(api_client):
    # pass
    doctor = Doctor.objects.first()
    refresh = CustomRefreshToken.for_user(doctor.user)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(refresh.access_token))
    url = reverse('core-api:doctors:doctor-profile', kwargs={'pk': doctor.user_id})
    response = api_client.get(url)

    assert response.status_code == 200

    # fail: 다른 의사의 정보를 열람할 경우
    other_doctor = Doctor.objects.last()
    refresh = CustomRefreshToken.for_user(other_doctor.user)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(refresh.access_token))
    url = reverse('core-api:doctors:doctor-profile', kwargs={'pk': doctor.user_id})
    response_fail = api_client.get(url)

    assert response_fail.status_code == 403


@pytest.mark.django_db
def test_core_api_doctor_profile_update_for_doctor(api_client, get_token_with_doctor):
    data = {'phone': '010-987-654', 'description': 'updated description'}

    # pass
    doctor, refresh = get_token_with_doctor
    old_phone, old_description = doctor.phone, doctor.description

    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(refresh.access_token))
    url = reverse('core-api:doctors:doctor-profile', kwargs={'pk': doctor.user_id})
    response = api_client.patch(url, data=data)

    assert response.status_code == 200
    assert response.data['phone'] != old_phone
    assert response.data['description'] != old_description

    # fail: 다른 의사의 정보를 수정할 경우
    other_doctor = Doctor.objects.last()
    refresh = CustomRefreshToken.for_user(other_doctor.user)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(refresh.access_token))
    url = reverse('core-api:doctors:doctor-profile', kwargs={'pk': doctor.user_id})
    response = api_client.patch(url, data={'phone': '010-987-654', 'description': 'updated description'})

    assert response.status_code == 403

    # fail: 담당 환자가 의사의 정보를 수정할 경우
    patient = doctor.patients.first()
    refresh = CustomRefreshToken.for_user(patient.user)
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(refresh.access_token))
    response = api_client.patch(url, data={'phone': '010-987-654', 'description': 'updated description'})

    assert response.status_code == 403


@pytest.mark.django_db
def test_core_api_patient_profile_detail_for_doctor(api_client, get_token_with_doctor):
    doctor, refresh = get_token_with_doctor
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(refresh.access_token))

    # pass
    patients = Patient.objects.filter(doctor_id=doctor.user_id)
    for patient_id in patients.values_list('user_id', flat=True):
        url = reverse('core-api:doctors:patient-profile', kwargs={'pk': patient_id})
        response = api_client.get(url)
        assert response.status_code == 200

    # fail: 담당 환자가 아닌 환자의 정보를 열람할 경우
    not_care_patients = Patient.objects.exclude(doctor_id=doctor.user_id)
    for patient_id in not_care_patients.values_list('user_id', flat=True):
        url = reverse('core-api:doctors:patient-profile', kwargs={'pk': patient_id})
        response = api_client.get(url)
        assert response.status_code == 403


@pytest.mark.django_db
def test_core_api_patient_profile_update_for_doctor(api_client, get_token_with_doctor):
    data = {'data': 'can not send data to patient profile'}

    # fail: 의사는 환자의 프로필을 수정할 수 없음
    doctor, refresh = get_token_with_doctor
    patient = Patient.objects.filter(doctor_id=doctor.user_id).first()
    not_care_patient = Patient.objects.exclude(doctor_id=doctor.user_id).first()

    for patient in (patient, not_care_patient):
        url = reverse('core-api:doctors:patient-profile', kwargs={'pk': patient.user_id})
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(refresh.access_token))
        response = api_client.patch(url, data=data)
        assert response.status_code == 405


@pytest.mark.django_db
def test_core_api_prescription_create(api_client, get_token_with_doctor, get_token_with_patient,
                                      ):
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

    # pass
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

    # fail: 환자가 접근할 경우
    patient_user, patient_refresh = get_token_with_patient
    url = reverse('core-api:doctors:prescription-create')
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(patient_refresh.access_token))
    response = api_client.post(url, data=data)

    assert response.status_code == 403

    # file cleanup
    doctor_files.hard_delete()


@pytest.mark.django_db
def test_core_api_prescription_detail_update(api_client, get_token_with_doctor, get_token_with_patient):
    # pass
    doctor, refresh = get_token_with_doctor  # user_id=2
    prescription = Prescription.objects.filter(writer_id=doctor.user_id).first()
    data = {'description': 'updated prescription'}

    url = reverse('core-api:doctors:prescription-detail', kwargs={'pk': prescription.id})
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(refresh.access_token))
    response = api_client.patch(url, data=data)

    assert response.status_code == 200
    assert response.data['description'] != prescription.description

    # fail: 환자가 접근할 경우
    patient, refresh = get_token_with_patient
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(refresh.access_token))
    response = api_client.patch(url, data=data)

    assert response.status_code == 403

    # fail: 다른 의사가 소견서에 접근할 경우
    not_owner = Doctor.objects.get(user_id=3)
    refresh = CustomRefreshToken.for_user(not_owner.user)
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(refresh.access_token))
    response = api_client.patch(url, data=data)

    assert response.status_code == 403


@pytest.mark.django_db
def test_core_api_file_prescription_detail_update(api_client, get_token_with_doctor):
    data = {
        'active': False,
        'uploaded': True
    }
    # pass
    doctor, refresh = get_token_with_doctor
    prescription = Prescription.objects.filter(writer_id=doctor.user_id).first()
    file_prescription_id, old_active, old_uploaded = FilePrescription.objects.filter(
        prescription_id=prescription.id).values_list('id', 'active', 'uploaded').first()
    # old_active, old_uploaded = file_prescription.
    common_url = reverse('core-api:doctors:file-prescription-detail', kwargs={'pk': file_prescription_id})
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(refresh.access_token))
    response = api_client.patch(common_url, data=data)

    assert response.status_code == 200
    assert response.data['active'] == data['active']  # read & write
    assert response.data['uploaded'] != data['uploaded']  # read only

    # fail: 다른 의사가 file-prescription 접근 및 수정할 경우
    not_owner = Doctor.objects.get(user_id=3)
    refresh = CustomRefreshToken.for_user(not_owner.user)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(refresh.access_token))
    patch_response = api_client.patch(common_url, data=data)
    get_response = api_client.get(common_url)

    assert patch_response.status_code == 403
    assert get_response.status_code == 403


@pytest.mark.django_db
def test_core_api_doctor_profile_detail_for_patient(api_client, get_token_with_doctor, get_token_with_patient):
    pass


@pytest.mark.django_db
def test_core_api_doctor_file_detail_update():
    pass
