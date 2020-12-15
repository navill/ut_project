from django.urls import path
from prescriptions.api import views

app_name = 'prescriptions-api'
urlpatterns = [
    path('', views.PrescriptionListCreateAPIView.as_view(), name='list-create'),
    path('<int:pk>', views.PrescriptionRetrieveUpdateAPIView.as_view(), name='detail-update'),
]
