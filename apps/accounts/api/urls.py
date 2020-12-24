from django.urls import path

from accounts.api import views
from accounts.api.views import DoctorSignUpAPIView, PatientSignUpAPIView
from accounts.views import home_views

app_name = 'api'
urlpatterns = [
    path('', home_views.home, name='home'),
    path('signup/doctor', DoctorSignUpAPIView.as_view(), name='api-signup-doctor'),
    path('signup/patient', PatientSignUpAPIView.as_view(), name='api-signup-patient'),
    path('doctors', views.DoctorListAPIView.as_view(), name='doctor-list'),
    path('doctors/<int:pk>', views.DoctorRetrieveUpdateAPIView.as_view(), name='doctor-detail-update'),
    path('patients', views.PatientListAPIView.as_view(), name='patient-list'),
    path('patients/<int:pk>', views.PatientRetrieveUpdateAPIView.as_view(), name='patient-detail-update'),
]
