from django.urls import path

from accounts.api import views
from accounts.api.views import DoctorSignUpAPIView, PatientSignUpAPIView

app_name = 'api'
urlpatterns = [
    # doctor
    path('doctors', views.DoctorListAPIView.as_view(), name='doctor-list'),
    path('doctors/<int:pk>', views.DoctorRetrieveAPIView.as_view(), name='doctor-detail'),
    path('doctors/<int:pk>/update', views.DoctorUpdateAPIView.as_view(), name='doctor-update'),
    path('signup/doctor', DoctorSignUpAPIView.as_view(), name='api-signup-doctor'),

    # patient
    path('patients', views.PatientListAPIView.as_view(), name='patient-list'),
    path('patients/<int:pk>', views.PatientRetrieveAPIView.as_view(), name='patient-detail'),
    path('patients/<int:pk>/update', views.PatientUpdateAPIView.as_view(), name='patient-update'),
    path('signup/patient', PatientSignUpAPIView.as_view(), name='api-signup-patient'),

    # choices
    path('choices/doctors', views.DoctorChoicesAPIView.as_view(), name='doctor-choices'),
    path('choices/patients', views.PatientChoicesAPIView.as_view(), name='patient-choices'),
]
