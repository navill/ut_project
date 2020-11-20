from django.urls import path, include

from accounts.views import home_views, views

app_name = 'accounts'
urlpatterns = [
    path('', home_views.home, name='home'),
    path('signup/', home_views.SignUpView.as_view(), name='signup'),
    path('signup/normal/', views.NormalSignUpView.as_view(), name='normal_signup'),
    path('signup/staff/', views.StaffSignUpView.as_view(), name='staff_signup'),

    path('staff/', include(([
                                path('list/', views.StaffListView.as_view(), name='list'),
                                # path('update/', ),
                                # path('detail/', ),
                            ], 'views'), namespace='staff')),

    path('normal/', include(([
                                 path('list/', views.NormalListView.as_view(), name='list'),
                                 # path('update/', ),
                                 # path('detail/', ),
                             ], 'views'), namespace='normal')),
]
