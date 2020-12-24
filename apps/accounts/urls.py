from django.urls import path, include

from accounts.views import home_views, views
from accounts.views.views import CeleryTestView

app_name = 'accounts'
urlpatterns = [
    path('home', home_views.home, name='home'),
    path('api/', include('accounts.api.urls', namespace='api')),
    path('signup', home_views.SignUpView.as_view(), name='signup'),
    path('signup/patient', views.PatientSignUpView.as_view(), name='patient_signup'),
    path('signup/doctor', views.DoctorSignUpView.as_view(), name='doctor_signup'),

    path('doctor/', include(([
                                path('list', views.DoctorListView.as_view(), name='list'),
                                path('update/<int:pk>', views.DoctorUpdateView.as_view(), name='update'),
                                path('detail/<int:pk>', views.DoctorDetailView.as_view(), name='detail'),
                            ], 'views'), namespace='doctor')),

    path('patient/', include(([
                                 path('list', views.PatientListView.as_view(), name='list'),
                                 path('update/<int:pk>', views.PatientUpdateView.as_view(), name='update'),
                                 path('detail/<int:pk>', views.PatientDetailView.as_view(), name='detail'),
                             ], 'views'), namespace='patient')),
    path('celery/test/', CeleryTestView.as_view()),
    # path('api', include('api.urls'), namespace='api')
]
