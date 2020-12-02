from django.urls import path, include

from accounts.views import home_views, views
from accounts.views.views import CeleryTestView

app_name = 'accounts'
urlpatterns = [
    path('', home_views.home, name='home'),
    path('signup/', home_views.SignUpView.as_view(), name='signup'),
    path('signup/normal/', views.NormalSignUpView.as_view(), name='normal_signup'),
    path('signup/staff/', views.StaffSignUpView.as_view(), name='staff_signup'),

    path('staff/', include(([
                                path('list/', views.StaffListView.as_view(), name='list'),
                                path('update/<int:pk>', views.StaffUpdateView.as_view(), name='update'),
                                path('detail/<int:pk>', views.StaffDetailView.as_view(), name='detail'),
                            ], 'views'), namespace='staff')),

    path('normal/', include(([
                                 path('list/', views.NormalListView.as_view(), name='list'),
                                 path('update/<int:pk>', views.NormalUpdateView.as_view(), name='update'),
                                 path('detail/<int:pk>', views.NormalDetailView.as_view(), name='detail'),
                             ], 'views'), namespace='normal')),
    path('celery/test/', CeleryTestView.as_view()),
]
