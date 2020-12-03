from django.urls import path

from accounts.views import home_views

aapp_name = 'api'
urlpatterns = [
    path('', home_views.home, name='home'),

]
