import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.reverse import reverse

from accounts.models import Doctor, BaseUser
from files.models import DataFile

"""
    path('files', DataFileListAPIView.as_view(), name='file-list'),
    path('files/<uuid:id>', DataFileRetrieveAPIView.as_view(), name='file-retrieve'),
    path('files/upload', DoctorDataFileUploadAPIView.as_view(), name='file-upload'),
    path('files/download/<uuid:id>', DataFileDownloadAPIView.as_view(), name='file-download'),
    path('uploaded-list', UploadedFileListAPIView.as_view(), name='file-not-checked'
"""


@pytest.mark.django_db
def test_api_view_data_file_list(api_client_with_token_auth, data_file_bundle_by_doctor):
    url = reverse('files:file-list')
    response = api_client_with_token_auth.get(url, format='json')
    assert response.status_code == 200
    assert len(response.data) == 5


# @pytest.mark.django_db
# def test_api_create_data_file(api_client_with_token_auth, prescription):
#     upload_file = SimpleUploadedFile("file.txt", b"test file", content_type='multipart/form-data')
#     value = {
#         'prescription': prescription.id,
#         'file': upload_file
#     }
#     url = reverse('files:file-upload')
#     response = api_client_with_token_auth.post(url, data=value, format='multipart')
#     assert response.status_code == 201
#     assert 'txt/doctortest.com_file' in response.data['file']

#
@pytest.mark.django_db
def test_api_retrieve_data_file(api_client_with_token_auth, data_file_bundle_by_doctor):
    data_file = DataFile.objects.first()
    url = reverse('files:file-retrieve', kwargs={'id': data_file.id})
    response = api_client_with_token_auth.get(url, format='json')
    assert response.status_code == 200
    assert response.data.get('id', None) is None
    assert response.data['url'] == 'http://testserver/datafiles/files/' + str(data_file.id)
    assert response.data['prescription'] == 1
