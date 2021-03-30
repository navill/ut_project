from django.urls import path
from prescriptions.api import views

app_name = 'prescriptions-api'
urlpatterns = [
    path('', views.PrescriptionListAPIView.as_view(),
         name='prescription-list'),
    path('create', views.PrescriptionCreateAPIView.as_view(),
         name='prescription-create'),
    path('<int:pk>', views.PrescriptionRetrieveAPIView.as_view(),
         name='prescription-detail'),
    path('<int:pk>/update', views.PrescriptionUpdateAPIView.as_view(),
         name='prescription-update'),
    path('file-prescriptions', views.FilePrescriptionListAPIView.as_view(),
         name='file-prescription-list'),
    path('file-prescriptions/create', views.FilePrescriptionCreateAPIView.as_view(),
         name='file-prescription-list'),
    path('file-prescriptions/<int:pk>', views.FilePrescriptionRetrieveAPIView.as_view(),
         name='file-prescription-detail'),
    path('file-prescriptions/<int:pk>/update', views.FilePrescriptionUpdateAPIView.as_view(),
         name='file-prescription-update'),

    path('choices/prescriptions', views.PrescriptionChoiceAPIView.as_view(),
         name='choice-prescription'),
    path('choices/file-prescriptions', views.FilePrescriptionChoiceAPIView.as_view(),
         name='choice-file-prescription')
]
