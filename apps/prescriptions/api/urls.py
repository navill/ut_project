from django.urls import path
from prescriptions.api import views

app_name = 'prescriptions-api'
urlpatterns = [
    path('', views.PrescriptionListCreateAPIView.as_view(), name='prescription-list-create'),
    path('<slug:slug>', views.PrescriptionRetrieveUpdateAPIView.as_view(), name='prescription-detail-update'),
]
