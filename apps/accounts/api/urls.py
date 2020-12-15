from django.urls import path, include

from accounts.api import views
from accounts.api.views import DoctorSignUpAPIView, PatientSignUpAPIView

app_name = 'accounts-api'
urlpatterns = [
    # path('', home_views.home, name='home'),
    path('signup/doctor', DoctorSignUpAPIView.as_view(), name='api-signup'),
    path('signup/patient', PatientSignUpAPIView.as_view(), name='api-signup'),
    path('doctors', include(([
                                 path('', views.DoctorListAPIView.as_view(), name='list'),
                                 path('<int:pk>', views.DoctorDetailUpdateAPIView.as_view(), name='detail-update'),
                                 # path('detail/<int:pk>', views.DoctorDetailUpdateAPIView.as_view(), name='detail'),
                                 # path('<int:pk>', views.DoctorDetailUpdateAPIView.as_view(), name='get-put-doctor'),
                             ], 'views'), namespace='doctor')),
    #
    path('patients', include(([
                                  path('', views.PatientListAPIView.as_view(), name='list'),
                                  path('<int:pk>', views.PatientDetailUpdateAPIView.as_view(), name='update'),
                              ], 'views'), namespace='patient')),
]
