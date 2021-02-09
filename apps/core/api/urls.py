from django.urls import path, include

from core.api import views

app_name = 'core'
urlpatterns = [
    # doctor
    path('doctors/', include(([path('<int:pk>/patients',  # 0
                                    views.DoctorNestedPatients.as_view(),
                                    name='detail'),

                               path('patients/<int:pk>/prescriptions',  # 1
                                    views.PatientNestedPrescriptions.as_view(),
                                    name='prescription-list'),

                               path('prescription-nested-files/<int:pk>/file-prescriptions',  # 2
                                    views.PrescriptionNestedFilePrescriptions.as_view(),
                                    name='prescription-detail'),

                               path('file-prescriptions/<int:pk>/patient-files',  # 3
                                    views.FilePrescriptionNestedPatientFiles.as_view(),
                                    name='file-prescription-list'),

                               # main - detail
                               path('<int:pk>/detail',
                                    views.DoctorProfile.as_view(),
                                    name='doctor-profile'),
                               path('patient/<int:pk>/detail',
                                    views.PatientProfile.as_view(),
                                    name='patient-profile'),
                               path('prescriptions/create',
                                    views.PrescriptionCreate.as_view(),
                                    name='prescription-create'),
                               path('prescriptions/<int:pk>',
                                    views.PrescriptionDetail.as_view(),
                                    name='prescription-detail'),
                               path('file-prescription/<int:pk>',
                                    views.FilePrescriptionDetail.as_view(),
                                    name='file-prescription-detail'),
                               path('doctor-files/upload',
                                    views.DoctorFileUpload.as_view(),
                                    name='file-upload'),
                               path('doctor-files/<int:pk>',
                                    views.DoctorFileDetail.as_view(),
                                    name='file-detail'),

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

                                path('file-prescriptions',  # only patient
                                     views.FilePrescriptionListForPatient.as_view(),
                                     name='file-prescription-list'),

                                path('file-prescriptions/<int:pk>',  # detail(owner readonly)
                                     views.FilePrescriptionDetailForPatient.as_view(),
                                     name='file-prescription-detail'),

                                path('main/<int:pk>',
                                     views.PatientMain.as_view(),
                                     name='main'),

                                # main - detail
                                path('<int:pk>/detail',
                                     views.PatientProfileForPatient.as_view(),
                                     name='patient-detail'),

                                path('doctors/<int:pk>/detail',
                                     views.DoctorProfileForPatient.as_view,
                                     name='doctor-detail'),

                                path('patient-files/upload',
                                     views.PatientFileUpload.as_view(),
                                     name='file-upload'),

                                path('patient-files/<int:pk>/detail',
                                     views.PatientFileDetailForPatient.as_view(),
                                     name='file-detail')

                                ], 'views'), namespace='patients')),
]

# temp = [
#     path('doctors/<int:pk>/patients', views.DoctorNestedPatients.as_view(),
#          name='doctor-with-patients'),
#     path('patients/<int:pk>/prescriptions', views.PatientNestedPrescriptions.as_view(),
#          name='patient-with-prescriptions'),
#     path('prescription-nested-files/<int:pk>/file-prescriptions', views.PrescriptionNestedFilePrescriptions.as_view(),
#          name='prescription-detail'),
#     path('file-prescriptions/<int:pk>/patient-files', views.FilePrescriptionNestedPatientFiles.as_view(),
#          name='file-prescription-detail'),

# doctor-main histories

# path('', views.xx.as_view(), name=''),  #
# path('', views.xx.as_view(), name=''),  #
# ]
