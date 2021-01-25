from django.urls import path

from core.api import views

app_name = 'api'
urlpatterns = [
    # doctor-main url
    path('doctors/<int:pk>/patients', views.DoctorNestedPatients.as_view(),
         name='doctor-with-patients'),  #
    path('patients/<int:pk>/prescriptions', views.PatientNestedPrescriptions.as_view(),
         name='patient-with-prescriptions'),  #
    path('doctors/<int:pk>', views.DoctorUpdate.as_view(),
         name='doctor-retrieve-update'),  # [GET, PATCH]
    path('prescription-nested-files/<int:pk>/file-prescriptions', views.PrescriptionNestedFilePrescriptions.as_view(),
         name='prescription-detail'),  #
    path('file-prescriptions/<int:pk>/patient-files', views.FilePrescriptionNestedPatientFiles.as_view(),
         name='file-prescription-detail'),  #
    path('file-prescriptions/new-uploaded-file', views.PatientFileHistoryInFilePrescription.as_view(),
         name='new-patient-file')
    # path('', views.xx.as_view(), name=''),  #
    # path('', views.xx.as_view(), name=''),  #
    # path('', views.xx.as_view(), name=''),  #
]
