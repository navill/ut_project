from django.urls import path
from prescriptions.api import views

app_name = 'prescriptions-api'
urlpatterns = [
    path('', views.PrescriptionListAPIView.as_view(), name='prescription-list'),
    path('create', views.PrescriptionCreateAPIView.as_view(), name='prescription-create'),
    path('<int:pk>', views.PrescriptionRetrieveAPIView.as_view(), name='prescription-detail'),
    path('<int:pk>/update', views.PrescriptionUpdateAPIView.as_view(), name='prescription-update'),
    path('file-pres', views.FilePrescriptionListAPIView.as_view(), name='file-prescription-list'),
    path('file-pres/create', views.FilePrescriptionCreateAPIView.as_view(), name='file-prescription-list'),
    path('file-pres/<int:pk>', views.FilePrescriptionRetrieveAPIView.as_view(), name='file-prescription-detail'),
    path('file-pres/<int:pk>/update', views.FilePrescriptionUpdateAPIView.as_view(), name='file-prescription-update')

    # path('file-pres/histories', views...)
    # path('test-pres/<int:pk>', views.TestPrescriptionAPIView.as_view())
]
