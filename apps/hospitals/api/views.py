from rest_framework import generics
from rest_framework.permissions import AllowAny

from hospitals.api import serializers
from hospitals.models import MedicalCenter, Department, Major

"""
Related Hospital view 
"""


class MedicalCenterNestedChildAllList(generics.ListAPIView):
    queryset = MedicalCenter.objects.prefetch_all()
    serializer_class = serializers.MedicalCenterNestedDepartmentMajor
    permission_classes = [AllowAny]


class DepartmentNestedChildList(generics.ListAPIView):
    queryset = Department.objects.prefetch_all()
    serializer_class = serializers.DepartmentNestedMajor
    permission_classes = [AllowAny]


"""
MedicalCenter CRUDL View
"""


class MedicalCenterListAPIView(generics.ListAPIView):
    queryset = MedicalCenter.objects.all()
    serializer_class = serializers.MedicalCenterListSerializer
    permission_classes = [AllowAny]


class MedicalCenterCreateAPIView(generics.CreateAPIView):
    serializer_class = serializers.MedicalCenterCreateSerializer
    permission_classes = [AllowAny]  # IsSuperuser


class MedicalCenterRetrieveAPIView(generics.RetrieveUpdateAPIView):
    queryset = MedicalCenter.objects.all()
    serializer_class = serializers.MedicalCenterRetrieveSerializer
    permission_classes = [AllowAny]  # IsSuperuser


class MedicalCenterUpdateAPIView(generics.UpdateAPIView):
    queryset = MedicalCenter.objects.all()
    serializer_class = serializers.MedicalCenterRetrieveSerializer
    permission_classes = [AllowAny]  # IsSuperuser


"""
Department CRUDL view
"""


class DepartmentListAPIView(generics.ListAPIView):
    queryset = Department.objects.select_all()
    serializer_class = serializers.DepartmentListSerializer
    permission_classes = [AllowAny]


class DepartmentCreateAPIView(generics.CreateAPIView):
    serializer_class = serializers.DepartmentCreateSerializer
    permission_classes = [AllowAny]  # IsSuperuser


class DepartmentRetrieveAPIView(generics.RetrieveUpdateAPIView):
    queryset = Department.objects.select_all()
    serializer_class = serializers.DepartmentRetreiveSerializer
    permission_classes = [AllowAny]  # IsSuperuser


class DepartmentUpdateAPIView(generics.UpdateAPIView):
    queryset = Department.objects.select_all()
    serializer_class = serializers.DepartmentRetreiveSerializer
    permission_classes = [AllowAny]  # IsSuperuser


"""
Major CRUDL view
"""


class MajorListAPIView(generics.ListAPIView):
    queryset = Major.objects.select_all()
    serializer_class = serializers.MajorListSerializer
    permission_classes = [AllowAny]


class MajorCreateAPIView(generics.CreateAPIView):
    serializer_class = serializers.MajorCreateSerializer
    permission_classes = [AllowAny]  # IsSuperuser


class MajorRetrieveAPIView(generics.RetrieveUpdateAPIView):
    queryset = Major.objects.select_all()
    serializer_class = serializers.MajorRetrieveSerializer
    permission_classes = [AllowAny]  # IsSuperuser


class MajorUpdateAPIView(generics.UpdateAPIView):
    queryset = Major.objects.select_all()
    serializer_class = serializers.MajorRetrieveSerializer
    permission_classes = [AllowAny]  # IsSuperuser
