from django.urls import path, include

from accounts.api import views
from accounts.api.views import DoctorSignUpAPIView, PatientSignUpAPIView

app_name = 'api'
urlpatterns = [
    # path('', home_views.home, name='home'),
    path('signup/doctor', DoctorSignUpAPIView.as_view(), name='api-signup'),
    path('signup/patient', PatientSignUpAPIView.as_view(), name='api-signup'),
    path('doctor/', include(([
                                 path('list', views.DoctorListAPIView.as_view(), name='list'),
                                 path('update/<int:pk>', views.DoctorUpdateAPIView.as_view(), name='update'),
                                 path('detail/<int:pk>', views.DoctorDetailAPIView.as_view(), name='detail'),
                             ], 'views'), namespace='doctor')),
    #
    path('patient/', include(([
                                  path('list', views.PatientListAPIView.as_view(), name='list'),
                                  path('update/<int:pk>', views.PatientUpdateAPIView.as_view(), name='update'),
                                  path('detail/<int:pk>', views.PatientDetailAPIView.as_view(), name='detail'),
                              ], 'views'), namespace='patient')),
]