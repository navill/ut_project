from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny

from hospitals.api.serializers import DepartmentSerializer, MedicalCenterSerializer, MajorSerializer, \
    MedicalCenterNestedDepartmentMajor, MedicalCenterRetrieveSerializer, DepartmentRetreiveSerializer, \
    MajorRetrieveSerializer
from hospitals.models import MedicalCenter, Department, Major


class HospitalAPIView(ListCreateAPIView):
    queryset = MedicalCenter.objects.all()
    serializer_class = MedicalCenterNestedDepartmentMajor
    permission_classes = [AllowAny]


class MedicalCenterAPIView(ListCreateAPIView):
    queryset = MedicalCenter.objects.all()
    serializer_class = MedicalCenterSerializer
    permission_classes = [AllowAny]


class MedicalCenterRetrieveAPIView(RetrieveAPIView):
    queryset = MedicalCenter.objects.all()
    serializer_class = MedicalCenterRetrieveSerializer
    permission_classes = [AllowAny]


class DepartmentAPIView(ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [AllowAny]


class DepartmentRetrieveAPIView(RetrieveAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentRetreiveSerializer
    permission_classes = [AllowAny]


class MajorAPIView(ListCreateAPIView):
    queryset = Major.objects.all()
    serializer_class = MajorSerializer
    permission_classes = [AllowAny]


class MajorRetrieveAPIView(RetrieveAPIView):
    queryset = Major.objects.all()
    serializer_class = MajorRetrieveSerializer
    permission_classes = [AllowAny]
