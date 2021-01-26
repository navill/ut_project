from django.urls import path

from core.api import views

app_name = 'api'
urlpatterns = [
    # doctor-main url
    path('doctors/<int:pk>/patients', views.DoctorNestedPatients.as_view(),
         name='doctor-with-patients'),  #
    path('patients/<int:pk>/prescriptions', views.PatientNestedPrescriptions.as_view(),
         name='patient-with-prescriptions'),  #
    path('prescription-nested-files/<int:pk>/file-prescriptions', views.PrescriptionNestedFilePrescriptions.as_view(),
         name='prescription-detail'),  #
    path('file-prescriptions/<int:pk>/patient-files', views.FilePrescriptionNestedPatientFiles.as_view(),
         name='file-prescription-detail'),  #

    # doctor-main histories
    path('histroies/new-uploaded-file', views.UploadedPatientFileHistory.as_view(),
         name='new-patient-file'),
    path('histories/file-prescriptions/expired-upload-date', views.ExpiredFilePrescriptionHistory.as_view(),
         name='expired-date'),  #
    # path('', views.xx.as_view(), name=''),  #
    # path('', views.xx.as_view(), name=''),  #
]
