from django.urls import path
from prescriptions.api import views

app_name = 'prescriptions-api'
urlpatterns = [
    path('', views.PrescriptionListAPIView.as_view(), name='prescription-list'),
    path('create', views.PrescriptionCreateAPIView.as_view(), name='prescription-create'),

    # path('create', views.PrescriptionCreateAPIView.as_view(), name='prescription-crelate'),
    path('<int:pk>', views.PrescriptionRetrieveUpdateAPIView.as_view(), name='prescription-detail-update'),
    path('file-pres', views.FilePrescriptionListAPIView.as_view(), name='file-prescription-list'),
    path('file-pres/create', views.FilePrescriptionCreateAPIView.as_view(), name='file-prescription-list'),
    path('file-pres/<int:pk>', views.FilePrescriptionRetrieveUpdateAPIView.as_view(),
         name='file-prescription-detail-update'),
    # path('file-pres/histories', views...)
    # path('test-pres/<int:pk>', views.TestPrescriptionAPIView.as_view())
]
