from django.urls import path
from prescriptions.api import views

app_name = 'prescriptions-api'
urlpatterns = [
    path('', views.PrescriptionListCreateAPIView.as_view(), name='prescription-list'),
    path('<int:pk>', views.PrescriptionRetrieveUpdateAPIView.as_view(), name='prescription-detail-update'),
    path('file-pres', views.FilePrescriptionListAPIView.as_view(), name='file-prescription-list'),
    path('file-pres/<int:pk>', views.FilePrescriptionRetrieveUpdateAPIView.as_view(),
         name='file-prescription-detail-update'),
]
