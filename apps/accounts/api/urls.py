from django.urls import path, include

from accounts.api import views
from accounts.api.views import DoctorSignUpAPIView, PatientSignUpAPIView
from accounts.views import home_views

app_name = 'accounts-api'
urlpatterns = [
    path('', home_views.home, name='home'),
    path('signup/doctor', DoctorSignUpAPIView.as_view(), name='api-signup'),
    path('signup/patient', PatientSignUpAPIView.as_view(), name='api-signup'),
    path('doctors', views.DoctorListAPIView.as_view(), name='doctor-list'),
    path('doctors/<int:pk>', views.DoctorDetailUpdateAPIView.as_view(), name='doctor-detail-update'),
    path('patients', views.PatientListAPIView.as_view(), name='patient-list'),
    path('patients/<int:pk>', views.PatientDetailUpdateAPIView.as_view(), name='patient-detail-update'),
]
