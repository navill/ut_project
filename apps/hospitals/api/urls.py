from django.urls import path

from hospitals.api import views

app_name = 'hospitals-api'
urlpatterns = [
    path('medical-centers', views.MedicalCenterListAPIView.as_view(), name='medicalcenter-list'),
    path('medical-centers/<int:pk>', views.MedicalCenterRetrieveAPIView.as_view(), name='medicalcenter-retrieve'),
    path('medical-centers/<int:pk>/update', views.MedicalCenterUpdateAPIView.as_view(), name='medicalcenter-update'),

    path('medical-centers/create', views.MedicalCenterCreateAPIView.as_view(), name='medicalcenter-create'),

    path('departments', views.DepartmentListAPIView.as_view(), name='department-list'),
    path('departments/<int:pk>', views.DepartmentRetrieveAPIView.as_view(), name='department-retrieve'),
    path('dpeartments/<int:pk>/update', views.DepartmentUpdateAPIView.as_view(), name='department-update'),
    path('departments/create', views.DepartmentCreateAPIView.as_view(), name='department-create'),

    path('majors', views.MajorListAPIView.as_view(), name='major-list'),
    path('majors/<int:pk>', views.MajorRetrieveAPIView.as_view(), name='major-retrieve'),
    path('majors/create', views.MajorCreateAPIView.as_view(), name='major-create'),

    # nested view
    # path('department-nested', views.DepartmentNestedChildList.as_view(), name='department-nested-major'),
    path('hospitals/choices/medical-centers', views.MedicalCenterChoiceAPIView),
    # path('hospitals/choices/departments'),
    # path('hospitals/choices/majors'),

    # choices
    path('choices/medical-centers', views.MedicalCenterChoiceAPIView.as_view(),
         name='medicalcenter-choices'),
    path('choices/departments', views.DepartmentChoiceAPIView.as_view(),
         name='department-choices'),
    path('choices/majors', views.MajorChoiceAPIView.as_view(),
         name='major-choices'),
]
