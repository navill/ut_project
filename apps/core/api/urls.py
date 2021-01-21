from django.urls import path

from files.api import views

app_name = 'api'
urlpatterns = [
    # common url
    path('logout', views.logout.as_view()),

    # doctor-main url
    path('doctors/<int:pk>/patients', views.DoctorNestedPatients.as_view(), name='doctor-file-list'),  #
    path('doctors/<int:pk>/patients/<int:pk>/prescriptions', views.PatientNestedPrescriptions.as_view(), name=''),  #
    path('doctors/<int:pk>', views.DoctorUpdate.as_view(), name=''),  # [GET, PATCH]
    path('prescription-nested-files/<int:pk>/file-prescriptions',
         views.PrescriptionNestedFilePrescriptions.as_view(), name=''),  #
    path('prescriptions/<int:pk>/file-pres/<int:pk>/patient-files',
         views.FilePrescriptionNestedPatientFiles.as_view(), name=''),  #

    path('', views.xx.as_view(), name=''),  #
    path('', views.xx.as_view(), name=''),  #
    path('', views.xx.as_view(), name=''),  #

]
