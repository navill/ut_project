import pytest
from rest_framework.reverse import reverse

from files.models import DataFile, HealthStatus
from tests.constants import User

"""
    path('doctor-files', DoctorDataFileListAPIView.as_view(), name='doctor-file-list'),
    path('doctor-files/upload', DoctorDataFileUploadAPIView.as_view(), name='doctor-file-upload'),
    path('doctor-uploaded-files', DoctorUploadedFileListAPIView.as_view(), name='doctor-file-not-checked'),
    path('doctor-uploaded-files/<uuid:id>', DoctorUploadedFileUpdateAPIView.as_view(), name='file-status-update'),

    path('patient-files', PatientDataFileListAPIView.as_view(), name='patient-file-list'),
    path('patient-files/upload', PatientDataFileUploadAPIView.as_view(), name='patient-file-upload'),
    path('patient-uploaded-files', PatientUploadedFileListAPIView.as_view(), name='patient-file-not-checked'),

    path('files/<uuid:id>', DataFileRetrieveAPIView.as_view(), name='file-retrieve'),
    path('files/download/<uuid:id>', DataFileDownloadAPIView.as_view(), name='file-download'))
"""


@pytest.mark.django_db
def test_api_view_data_file_list_by_doctor(api_client, doctors_with_group, doctor_client_with_token_auth,
                                           data_file_bundle_by_doctor):
    url = reverse('files:doctor-file-list')
    response = doctor_client_with_token_auth.get(url, format='json')
    assert response.status_code == 200
    assert len(response.data) == 5


@pytest.mark.django_db
def test_api_create_data_file_by_doctor(doctor_client_with_token_auth, prescription, upload_file):
    value = {
        'prescription': prescription.id,
        'file': upload_file,
        'status': HealthStatus.NORMAL
    }
    url = reverse('files:doctor-file-upload')
    response = doctor_client_with_token_auth.post(url, data=value, format='multipart')
    assert response.status_code == 201


@pytest.mark.django_db
def test_api_retrieve_data_file_by_doctor(doctor_client_with_token_auth, data_file_bundle_by_doctor):
    data_file = DataFile.objects.first()
    url = reverse('files:file-retrieve', kwargs={'id': data_file.id})
    response = doctor_client_with_token_auth.get(url, format='json')
    assert response.status_code == 200
    assert response.data.get('id', None) is None
    assert response.data['url'] == 'http://testserver/datafiles/files/' + str(data_file.id)
    assert response.data['prescription'] == 1


@pytest.mark.django_db
def test_api_view_uploaded_file_list_by_doctor(doctor_client_with_token_auth, data_file_bundle_by_doctor):
    url = reverse('files:doctor-file-not-checked')
    data_file = DataFile.objects.all()
    response = doctor_client_with_token_auth.get(url, format='json')
    assert data_file.count() == 5
    assert response.status_code == 200
    assert len(response.data) == 0


@pytest.mark.django_db
def test_api_view_data_file_list_by_patient(patient_client_with_token_auth, data_file_bundle_by_patient):
    url = reverse('files:patient-file-list')
    response = patient_client_with_token_auth.get(url, format='json')
    assert response.status_code == 200
    assert len(response.data) == 5


@pytest.mark.django_db
def test_api_create_data_file_by_patient(patient_client_with_token_auth, prescription, upload_file):
    value = {
        'prescription': prescription.id,
        'file': upload_file,
        'status': HealthStatus.NORMAL
    }
    url = reverse('files:patient-file-upload')
    response = patient_client_with_token_auth.post(url, data=value, format='multipart')
    assert response.status_code == 201


@pytest.mark.django_db
def test_api_retrieve_data_file_by_patient(patient_client_with_token_auth, data_file_bundle_by_patient):
    data_file = DataFile.objects.first()
    url = reverse('files:file-retrieve', kwargs={'id': data_file.id})
    response = patient_client_with_token_auth.get(url, format='json')
    assert response.status_code == 200
    assert response.data.get('id', None) is None
    assert response.data['url'] == 'http://testserver/datafiles/files/' + str(data_file.id)
    assert response.data['prescription'] == 1


@pytest.mark.django_db
def test_api_view_uploaded_file_list_by_patient(patient_client_with_token_auth, data_file_bundle_by_patient):
    url = reverse('files:patient-file-not-checked')
    data_file = DataFile.objects.all()
    response = patient_client_with_token_auth.get(url, format='json')
    assert data_file.count() == len(response.data)
    assert response.status_code == 200
