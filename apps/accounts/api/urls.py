from django.urls import path

from accounts.api import views
from accounts.api.views import DoctorSignUpAPIView, PatientSignUpAPIView

app_name = 'api'
urlpatterns = [
    path('signup/doctor', DoctorSignUpAPIView.as_view(), name='api-signup-doctor'),
    path('signup/patient', PatientSignUpAPIView.as_view(), name='api-signup-patient'),
    path('doctors', views.DoctorListAPIView.as_view(), name='doctor-list'),
    path('doctors/<int:pk>', views.DoctorRetrieveAPIView.as_view(), name='doctor-detail'),
    path('doctors/<int:pk>/update', views.DoctorUpdateAPIView.as_view(), name='doctor-update'),
    path('patients', views.PatientListAPIView.as_view(), name='patient-list'),
    path('patients/<int:pk>', views.PatientRetrieveAPIView.as_view(), name='patient-detail'),
    path('patients/<int:pk>/update', views.PatientUpdateAPIView.as_view(), name='patient-update'),

]
