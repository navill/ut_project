import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.reverse import reverse

from accounts.api.authentications import CustomRefreshToken
from accounts.models import Doctor, Patient
from files.models import DoctorFile
from prescriptions.models import Prescription, FilePrescription


@pytest.mark.django_db
def test_create_and_update_prescription(api_client):
    # pass - prescription create
    doctor = Doctor.objects.get(user_id=2)
    token = CustomRefreshToken.for_user(doctor.user)
    # authenticate token
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token.access_token))
    patient = Patient.objects.get(user_id=5)
    url = reverse('prescriptions:prescription-create')
    file1 = SimpleUploadedFile('test_file1.md', b'test prescription 1', content_type='ultipart/form-data')
    file2 = SimpleUploadedFile('test_file2.md', b'test prescription 2', content_type='multipart/form-data')
    value = {
        "description": "new test",
        "patient": patient.user_id,
        "doctor_upload_files": [file1, file2],
        "start_date": '2021-02-01',
        "end_date": '2021-02-10'
    }
    response = api_client.post(url, data=value, format='multipart')
    assert response.status_code == 201
    assert response.data['description'] == "new test"
    prescription = Prescription.objects.first()
    assert prescription.description == "new test"

    # 생성된 file prescription 확인
    fp = FilePrescription.objects.filter(prescription_id=prescription.id)
    assert fp.count() == 10
    assert fp.first().patient_id == patient.user_id and fp.last().patient_id == patient.user_id
    assert fp.first().writer_id == doctor.user_id and fp.last().writer_id == doctor.user_id
    assert fp.first().day_number == 10 and fp.last().day_number == 1

    # 생성된 doctor file 확인
    doctor_files = DoctorFile.objects.filter(prescription_id=prescription.id)
    assert doctor_files.count() == 2
    assert "test_file2.md" in doctor_files.first().file.name and "test_file1.md" in doctor_files.last().file.name

    # pass - file update
    update_url = reverse('prescriptions:prescription-update', kwargs={'pk': prescription.id})
    test_file = SimpleUploadedFile('updated_file1.md', b'update prescription', content_type='multipart/form-data')
    updated_value = {
        "description": "updated description",
        "doctor_upload_files": [test_file],
    }
    response = api_client.put(update_url, data=updated_value, formart='multipart')
    assert response.status_code == 200
    assert response.data['description'] == updated_value['description']
    assert len(response.data['doctor_files']) == 1
    assert prescription.doctor_files.filter_not_deleted().count() == 1
    assert prescription.file_prescriptions.filter(deleted=False).count() == 10  # 수정전 FilePrescription 객체의 수

    # pass - file prescription update
    update_url = reverse('prescriptions:prescription-update', kwargs={'pk': prescription.id})
    updated_value = {
        "description": "file prescription update",
        "start_date": "2021-03-03",
        "end_date": "2021-03-06"
    }
    response = api_client.put(update_url, data=updated_value, formart='multipart')
    assert response.status_code == 200
    assert response.data['description'] == updated_value['description']
    assert prescription.file_prescriptions.count() == 4  # 수정된 FilePrescription 객체의 수
    # cleanup(fixture cleanup -> yield): 테스트 파일 삭제
    for file in DoctorFile.objects.filter(prescription_id=prescription.id):
        file.hard_delete()


@pytest.mark.django_db
def test_prescription_list(api_client):
    # pass
    doctor = Doctor.objects.get(user_id=2)
    token = CustomRefreshToken.for_user(doctor.user)
    url = reverse('prescriptions:prescription-list')

    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token.access_token))
    response = api_client.get(url)
    assert response.status_code == 200
    result_data = response.data['results'][0]
    result_dic = {key: value for key, value in result_data.items() if key == 'writer_id'}

    # pass: 접근한 의사 계정으로 작성한 prescription만 출력되는지 테스트
    for writer_id in result_dic.values():
        assert writer_id == doctor.user_id

    # pass: 환자 계정으로 접근 + 자신과 관련된 소견서 리스트
    patient = Patient.objects.first()
    token = CustomRefreshToken.for_user(patient.user)
    url = reverse('prescriptions:prescription-list')

    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token.access_token))
    response = api_client.get(url)
    assert response.status_code == 200

    result_list = response.data['results']
    for result in result_list:
        patient_id = result['patient']
        assert patient.user_id == patient_id

    # prescription-list 결과와 환자 계정으로 필터링된 Prescription 모델 수 비교
    prescription_count = Prescription.objects.filter(patient_id=patient.user_id).count()
    assert prescription_count == len(result_list)

    # fail: 미인증
    api_client.credentials()
    response = api_client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_prescription_detail(api_client):
    # prescription.writer_id=2, prescription.patient_id=5
    doctor = Doctor.objects.get(user_id=2)
    patient = Patient.objects.get(user_id=5)

    prescription = Prescription.objects.filter(writer_id=doctor.user_id).first()
    url = reverse('prescriptions:prescription-detail', kwargs={'pk': prescription.id})

    # pass: writer 접근
    token = CustomRefreshToken.for_user(doctor.user)
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token.access_token))
    response = api_client.get(url)
    assert response.status_code == 200
    update_url = response.data.get('url', None)
    assert update_url is not None

    # pass: patient 접근
    token = CustomRefreshToken.for_user(patient.user)
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token.access_token))
    response = api_client.get(url)
    assert response.status_code == 200
    update_url = response.data.get('url', None)
    assert update_url is None

    # fail: 잘못된 writer 접근
    other_doctor = Doctor.objects.get(user_id=3)
    token = CustomRefreshToken.for_user(other_doctor.user)
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token.access_token))
    response = api_client.get(url)
    assert response.status_code == 403

    # fail: 잘못된 patient 접근
    other_patient = Patient.objects.get(user_id=6)
    token = CustomRefreshToken.for_user(other_patient.user)
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token.access_token))
    response = api_client.get(url)
    assert response.status_code == 403

    # fail: 미인증
    api_client.credentials()
    response = api_client.get(url)
    assert response.status_code == 403


@pytest.mark.xfail
@pytest.mark.django_db
def test_file_prescription_list(api_client):
    pass


@pytest.mark.xfail
@pytest.mark.django_db
def test_file_prescription_detail(api_client):
    pass


@pytest.mark.xfail
@pytest.mark.django_db
def test_file_prescription_create_and_update(api_client):
    pass
