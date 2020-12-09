from django.urls import path, include

from accounts.api import views
from accounts.api.views import DoctorSignUpAPIView, PatientSignUpAPIView

app_name = 'api'
urlpatterns = [
    # path('', home_views.home, name='home'),
    path('signup/doctor', DoctorSignUpAPIView.as_view(), name='api-signup'),
    path('signup/patient', PatientSignUpAPIView.as_view(), name='api-signup'),
    # path('doctor/', include(([
    #                              path('list', views.DoctorListView.as_view(), name='list'),
    #                              path('update/<int:pk>', views.DoctorUpdateView.as_view(), name='update'),
    #                              path('detail/<int:pk>', views.DoctorDetailView.as_view(), name='detail'),
    #                          ], 'views'), namespace='doctor')),
    #
    # path('patient/', include(([
    #                               path('list', views.PatientListView.as_view(), name='list'),
    #                               path('update/<int:pk>', views.PatientUpdateView.as_view(), name='update'),
    #                               path('detail/<int:pk>', views.PatientDetailView.as_view(), name='detail'),
    #                           ], 'views'), namespace='patient')),
]