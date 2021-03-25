from django.urls import path

from files.api import views

app_name = 'api'
urlpatterns = [
    path('doctor-files', views.DoctorFileListAPIView.as_view(), name='doctor-file-list'),  #
    path('doctor-files/upload', views.DoctorFileUploadAPIView.as_view(), name='doctor-file-upload'),  #
    path('doctor-files/<uuid:id>', views.DoctorFileRetrieveAPIView.as_view(), name='doctor-file-retrieve'),  #
    path('doctor-files/<uuid:id>/update', views.DoctorFileUpdateAPIView.as_view(), name='doctor-file-update'),  #
    path('doctor-files/<uuid:id>/download', views.DoctorFileDownloadAPIView.as_view(), name='doctor-file-download'),  #

    path('patient-files', views.PatientFileListAPIView.as_view(), name='patient-file-list'),
    path('patient-files/upload', views.PatientFileUploadAPIView.as_view(), name='patient-file-upload'),
    path('patient-files/<uuid:id>', views.PatientFileRetrieveAPIView.as_view(), name='patient-file-retrieve'),  #
    path('patient-files/<uuid:id>/update', views.PatientFileUpdateAPIView.as_view(), name='patient-file-update'),  #
    path('patient-files/<uuid:id>/download', views.PatientFileDownloadAPIView.as_view(), name='patient-file-download'),  #

]
