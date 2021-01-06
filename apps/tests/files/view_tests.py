import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.reverse import reverse

from accounts.models import BaseUser
from config.settings.local import MEDIA_ROOT
from files.models import DataFile, HealthStatus
from tests.conftest import renew_generated_uuid
from tests.constants import DATAFILE

"""
    path('files', DataFileListAPIView.as_view(), name='file-list'),
    path('files/<uuid:id>', DataFileRetrieveAPIView.as_view(), name='file-retrieve'),
    path('files/upload', DoctorDataFileUploadAPIView.as_view(), name='file-upload'),
    path('files/download/<uuid:id>', DataFileDownloadAPIView.as_view(), name='file-download'),
    path('uploaded-list', UploadedFileListAPIView.as_view(), name='file-not-checked'
"""


@pytest.mark.django_db
def test_api_view_data_file_list(api_client, get_token_from_doctor, data_file_bundle_by_doctor):
    access = get_token_from_doctor.access_token
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(access))

    url = reverse('files:file-list')
    response = api_client.get(url, format='json')
    assert response.status_code == 200
    assert len(response.data) == 5


@pytest.mark.django_db
def test_api_create_data_file(api_client, get_token_from_doctor, prescription, user_doctor_with_group):
    access = get_token_from_doctor.access_token
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(access))

    upload_file = SimpleUploadedFile("file.txt", b"abc", content_type='multipart/form-data')
    value = {
        # 'uploader': user.id,
        'prescription': prescription.id,
        'file': upload_file
    }

    url = reverse('files:file-upload')
    response = api_client.post(url, data=value, format='multipart')
    assert response.status_code == 201
    assert 'txt/doctortest.com_file' in response.data['file']


@pytest.mark.django_db
def test_api_retrieve_data_file(api_client, get_token_from_doctor, data_file_bundle_by_doctor):
    access = get_token_from_doctor.access_token
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(access))

    data_file = DataFile.objects.first()
    url = reverse('files:file-retrieve', kwargs={'id': data_file.id})
    response = api_client.get(url, format='json')
    assert response.status_code == 200
    assert response.data.get('id', None) is None
    assert response.data['url'] == 'http://testserver/datafiles/files/' + str(data_file.id)
    assert response.data['prescription'] == 1
