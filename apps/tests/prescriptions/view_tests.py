import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.reverse import reverse

from accounts.models import Doctor, Patient
from files.models import DoctorFile
from prescriptions.models import Prescription, FilePrescription


def test_prescriptions_stored_in_test_db(db, django_db_setup):
    prescription = Prescription.objects.first()
    assert prescription.id
    assert prescription.status in ['NORMAL', 'ABNORMAL', 'UNKNOWN']
    assert prescription.deleted is False
    assert isinstance(prescription.writer, Doctor)
    assert isinstance(prescription.patient, Patient)

    prescriptions = Prescription.objects.select_all()
    for prescription in prescriptions:
        assert prescription.id
        assert prescription.status in ['NORMAL', 'ABNORMAL', 'UNKNOWN']
        assert prescription.deleted is False
        assert isinstance(prescription.writer, Doctor)
        assert isinstance(prescription.patient, Patient)


@pytest.mark.django_db
def test_create_and_update_prescription(api_client):
    # pass - prescription create
    doctor = Doctor.objects.get(user_id=2)
    api_client.force_authenticate(user=doctor.user)
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
        "update_files": [test_file],
    }
    response = api_client.put(update_url, data=updated_value, formart='multipart')
    assert response.status_code == 200
    assert response.data['description'] == updated_value['description']
    assert len(response.data['doctor_files']) == 1
    doctor_files = DoctorFile.objects.filter(prescription_id=prescription.id).filter_not_deleted()
    assert doctor_files.count() == 1
    assert prescription.file_prescriptions.count() == 10  # 수정전 FilePrescription 객체의 수

    # pass - file prescription update
    update_url = reverse('prescriptions:prescription-update', kwargs={'pk': prescription.id})
    updated_value = {
        "description": "updated description",
        "start_date": "2021-03-03",
        "end_date": "2021-03-06"
    }
    response = api_client.put(update_url, data=updated_value, formart='multipart')
    assert response.status_code == 200
    assert prescription.file_prescriptions.count() == 4  # 수정된 FilePrescription 객체의 수

    # cleanup(fixture cleanup -> yield): 테스트 파일 삭제
    for file in DoctorFile.objects.filter(prescription_id=prescription.id):
        file.hard_delete()
