from django.urls import path

from hospitals.api.views import DepartmentAPIView, MajorAPIView, MedicalCenterAPIView, MedicalCenterRetrieveAPIView, \
    DepartmentRetrieveAPIView, MajorRetrieveAPIView, HospitalAllDepthAPIView

app_name = 'hospitals-api'
urlpatterns = [
    path('medical-centers', MedicalCenterAPIView.as_view(), name='medicalcenter-list-create'),
    path('medical-centers/<int:pk>', MedicalCenterRetrieveAPIView.as_view(), name='medicalcenter-retrieve'),

    path('departments', DepartmentAPIView.as_view(), name='department-list-create'),
    path('departments/<int:pk>', DepartmentRetrieveAPIView.as_view(), name='department-retrieve'),

    path('majors', MajorAPIView.as_view(), name='major-list-create'),
    path('majors/<int:pk>', MajorRetrieveAPIView.as_view(), name='major-retrieve'),

    path('all-depth', HospitalAllDepthAPIView.as_view(), name='all-depth-in-hospital')
]
