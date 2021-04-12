import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.reverse import reverse

from accounts.api.authentications import CustomRefreshToken
from accounts.models import Doctor, Patient
from prescriptions.models import Prescription, FilePrescription


@pytest.mark.django_db
def test_core_doctor_detail_for_doctor(api_client):
    # pass
    doctor = Doctor.objects.first()
    token = CustomRefreshToken.for_user(doctor.user)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token.access_token))
    url = reverse('core-api:doctors:detail', kwargs={'pk': doctor.user_id})
    response = api_client.get(url)

    assert response.status_code == 200

    # fail: 다른 의사의 정보를 열람할 경우
    other_doctor = Doctor.objects.last()
    token = CustomRefreshToken.for_user(other_doctor.user)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token.access_token))
    url = reverse('core-api:doctors:detail', kwargs={'pk': doctor.user_id})
    response_fail = api_client.get(url)

    assert response_fail.status_code == 403


@pytest.mark.django_db
def test_core_patients_prescription_list_for_doctor(api_client):
    # pass
    doctor = Doctor.objects.first()
    patients = Patient.objects.filter(doctor_id=doctor.user_id)
    patient = patients.first()
    token = CustomRefreshToken.for_user(doctor.user)
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token.access_token))
    url = reverse('core-api:doctors:prescription-list', kwargs={'pk': patient.user_id})
    response = api_client.get(url)
    assert response.status_code == 200

    # fail - 담당 환자가 아닐 경우
    patients = Patient.objects.exclude(doctor_id=doctor.user_id)
    patient = patients.first()
    url = reverse('core-api:doctors:prescription-list', kwargs={'pk': patient.user_id})
    response = api_client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_core_prescriptions_with_file_prescription_for_doctor(api_client):
    doctor = Doctor.objects.first()
    patients = Patient.objects.filter(doctor_id=doctor.user_id)
    prescription = Prescription.objects.filter(patient_id=patients.first().user_id).first()
    token = CustomRefreshToken.for_user(doctor.user)

    # pass
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token.access_token))
    url = reverse('core-api:doctors:prescription-file', kwargs={'pk': prescription.id})
    response = api_client.get(url)
    assert response.status_code == 200

    # fail - 소견서 작성자가 다를 경우
    doctor = Doctor.objects.last()
    token = CustomRefreshToken.for_user(doctor.user)
    prescription = Prescription.objects.exclude(writer_id=doctor.user_id).first()

    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token.access_token))
    url = reverse('core-api:doctors:prescription-file', kwargs={'pk': prescription.id})
    response = api_client.get(url)
    assert response.status_code == 403

    # fail - 환자가 접근할 경우
    patient = patients.first()
    token = CustomRefreshToken.for_user(patient.user)
    prescription = Prescription.objects.filter(patient_id=patient.user_id).first()

    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token.access_token))
    url = reverse('core-api:doctors:prescription-file', kwargs={'pk': prescription.id})
    response = api_client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_core_file_prescription_with_files_for_doctor(api_client):
    # pass
    doctor = Doctor.objects.first()
    token = CustomRefreshToken.for_user(doctor.user)
    file_prescription = FilePrescription.objects.filter(user=doctor.user_id).first()

    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token.access_token))
    url = reverse('core-api:doctors:file-prescription-with-patient-file', kwargs={'pk': file_prescription.id})
    response = api_client.get(url)
    assert response.status_code == 200

    # fail - 다른 의사가 생성한 FilePrescription 객체에 접근할 경우
    file_prescription = FilePrescription.objects.exclude(user=doctor.user_id).first()

    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token.access_token))
    url = reverse('core-api:doctors:file-prescription-with-patient-file', kwargs={'pk': file_prescription.id})
    response = api_client.get(url)
    assert response.status_code == 403

    # fail - 환자가 접근할 경우
    patient = Patient.objects.first()
    token = CustomRefreshToken.for_user(patient.user)
    file_prescription = FilePrescription.objects.filter(patient_id=patient.user_id).first()

    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token.access_token))
    url = reverse('core-api:doctors:file-prescription-with-patient-file', kwargs={'pk': file_prescription.id})
    response = api_client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_core_history_uploaded_patient_file(api_client):
    # pass
    doctor = Doctor.objects.first()
    token = CustomRefreshToken.for_user(doctor.user)
    # 새로 업로드된 파일 필터 = checked=False, uploaded=True
    file_prescriptions = FilePrescription.objects.filter(user=doctor.user_id, checked=False, uploaded=True)
    file_prescriptions_count = file_prescriptions.count()
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token.access_token))
    url = reverse('core-api:doctors:new-patient-file')
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data['count'] == file_prescriptions_count

    # pass - 환자가 새로운 파일을 업로드 할 경우
    patient = Patient.objects.filter(doctor_id=doctor.user_id).first()
    patient_token = CustomRefreshToken.for_user(patient.user)
    file_prescription = FilePrescription.objects.filter(user=doctor.user_id, checked=True).first()
    file = SimpleUploadedFile('test_file.md', b'test histroy', content_type='multipart/form-data')

    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(patient_token.access_token))
    value = {
        'file_prescription': file_prescription.id,
        'file': file,
    }
    uploaded_url = reverse('files:patient-file-upload')
    response = api_client.post(uploaded_url, data=value, format='multipart')
    assert response.status_code == 201

    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token.access_token))
    url = reverse('core-api:doctors:new-patient-file')
    response = api_client.get(url)
    assert file_prescriptions.count() == file_prescriptions_count + 1
    assert response.data['count'] == file_prescriptions_count + 1

    # fail - 환자가 접근할 경우
    patient = Patient.objects.first()
    token = CustomRefreshToken.for_user(patient.user)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token.access_token))
    url = reverse('core-api:doctors:new-patient-file')
    response = api_client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_core_history_expired_file_prescription(api_client):
    pass
