from django.urls import path, include

from core.api import views

app_name = 'core'
urlpatterns = [
    # doctor
    path('doctors/', include(([path('<int:pk>/patients',  # 0
                                    views.DoctorWithPatients.as_view(),
                                    name='detail'),

                               path('patients/<int:pk>/prescriptions',  # 1
                                    views.PatientWithPrescriptions.as_view(),
                                    name='prescription-list'),

                               path('prescription-nested-files/<int:pk>/file-prescriptions',  # 2
                                    views.PrescriptionWithFilePrescriptions.as_view(),
                                    name='prescription-file'),

                               path('file-prescriptions/<int:pk>/patient-files',  # 3
                                    views.FilePrescriptionWithPatientFiles.as_view(),
                                    name='file-prescription-with-patient-file'),

                               # histroy
                               path('histories/new-uploaded-file',  # 4
                                    views.UploadedPatientFileHistory.as_view(),
                                    name='new-patient-file'),

                               path('histories/expired-upload-date',  # 5
                                    views.ExpiredFilePrescriptionHistory.as_view(),
                                    name='expired-date'),

                               ], 'views'), namespace='doctors')),

    # patient
    path('patients/', include(([path('<int:pk>',  # owner read only
                                     views.PatientWithDoctor.as_view(),
                                     name='patient-detail'),

                                path('prescriptions',  # only patient
                                     views.PrescriptionListForPatient.as_view(),
                                     name='prescription-list'),

                                path('presscriptions/<int:pk>',  # detail(owner readonly)
                                     views.PrescriptionDetailForPatient.as_view(),
                                     name='prescription-detail'),

                                path('prescriptions/<int:pk>/file-prescriptions',  # only patient
                                     views.FilePrescriptionListForPatient.as_view(),
                                     name='file-prescription-list'),

                                path('file-prescriptions/<int:pk>',  # detail(owner readonly)
                                     views.FilePrescriptionDetailForPatient.as_view(),
                                     name='file-prescription-detail'),

                                path('main/<int:pk>',
                                     views.PatientMain.as_view(),
                                     name='main'),
                                ], 'views'), namespace='patients')
         ),
]
