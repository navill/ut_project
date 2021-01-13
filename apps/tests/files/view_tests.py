import pytest
from rest_framework.reverse import reverse

from files.models import DataFile, HealthStatus

"""
    path('files', DoctorDataFileListAPIView.as_view(), name='doctor-file-list'),
    path('files/patients', PatientDataFileListAPIView.as_view(), name='patient-file-list'),
    path('files/<uuid:id>', DataFileRetrieveAPIView.as_view(), name='file-retrieve'),
    path('files/upload', DoctorDataFileUploadAPIView.as_view(), name='file-upload'),
    path('files/download/<uuid:id>', DataFileDownloadAPIView.as_view(), name='file-download'),
    path('uploaded-list', UploadedFileListAPIView.as_view(), name='file-not-checked')
"""


@pytest.mark.django_db
def test_api_view_data_file_list_by_doctor(doctor_client_with_token_auth, data_file_bundle_by_doctor):
    url = reverse('files:file-doctor-list')
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
    url = reverse('files:file-doctor-upload')
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
    url = reverse('files:file-not-checked')
    data_file = DataFile.objects.all()
    response = doctor_client_with_token_auth.get(url, format='json')
    assert data_file.count() == 5
    assert response.status_code == 200
    assert len(response.data) == 0


@pytest.mark.django_db
def test_api_view_data_file_list_by_patient(patient_client_with_token_auth, data_file_bundle_by_patient):
    url = reverse('files:file-patient-list')
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
    url = reverse('files:file-patient-upload')
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
    url = reverse('files:file-not-checked')
    data_file = DataFile.objects.all()
    response = patient_client_with_token_auth.get(url, format='json')
    assert data_file.count() == len(response.data)
    assert response.status_code == 200
