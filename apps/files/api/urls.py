from django.urls import path

from files.api.views import DataFileListAPIVIew, DoctorDataFileUploadAPIView, DataFileRetrieveAPIVIew, DataFileDownloadAPIView

app_name = 'api'
urlpatterns = [
    path('files', DataFileListAPIVIew.as_view(), name='file-list'),
    path('files/<uuid:id>', DataFileRetrieveAPIVIew.as_view(), name='file-retrieve'),
    path('files/upload', DoctorDataFileUploadAPIView.as_view(), name='file-upload'),
    path('files/download/<uuid:id>', DataFileDownloadAPIView.as_view(), name='file-download')
]
