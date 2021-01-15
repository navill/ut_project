from django.urls import path

from files.api.views import DoctorDataFileListAPIView, PatientDataFileListAPIView, DoctorDataFileUploadAPIView, \
    DataFileRetrieveAPIView, \
    DataFileDownloadAPIView, DoctorUploadedFileListAPIView, PatientDataFileUploadAPIView, \
    DoctorUploadedFileUpdateAPIView, PatientUploadedFileListAPIView

app_name = 'api'
urlpatterns = [
    path('doctor-files', DoctorDataFileListAPIView.as_view(), name='doctor-file-list'),
    path('doctor-files/upload', DoctorDataFileUploadAPIView.as_view(), name='doctor-file-upload'),
    path('doctor-uploaded-files', DoctorUploadedFileListAPIView.as_view(), name='doctor-file-not-checked'),
    path('doctor-uploaded-files/<uuid:id>', DoctorUploadedFileUpdateAPIView.as_view(), name='file-status-update'),

    path('patient-files', PatientDataFileListAPIView.as_view(), name='patient-file-list'),
    path('patient-files/upload', PatientDataFileUploadAPIView.as_view(), name='patient-file-upload'),
    path('patient-uploaded-files', PatientUploadedFileListAPIView.as_view(), name='patient-file-not-checked'),

    path('files/<uuid:id>', DataFileRetrieveAPIView.as_view(), name='file-retrieve'),
    path('files/download/<uuid:id>', DataFileDownloadAPIView.as_view(), name='file-download'),
    # path('patient-uploaded-files/<uuid:id>', DoctorUploadedFileUpdateAPIView.as_view(), name='file-status-update'),
]
