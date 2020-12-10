from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from accounts.api.permissions import OnlyDoctor
from accounts.api.serializers import DoctorSignUpSerializer, PatientSignUpSerializer, DoctorSerializer, \
    PatientSerializer
from accounts.models import Doctor, Patient


class DoctorSignUpAPIView(CreateAPIView):
    serializer_class = DoctorSignUpSerializer
    permission_classes = [AllowAny]


class DoctorListAPIView(ListAPIView):
    queryset = Doctor.objects.all().order_by('-user__date_joined')
    serializer_class = DoctorSerializer
    permission_classes = [OnlyDoctor]


class DoctorDetailAPIView(RetrieveAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [OnlyDoctor]


class DoctorUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [OnlyDoctor]


class PatientSignUpAPIView(CreateAPIView):
    serializer_class = PatientSignUpSerializer
    permission_classes = [AllowAny]


class PatientListAPIView(ListAPIView):
    queryset = Patient.objects.all().order_by('-user__date_joined')
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]


class PatientDetailAPIView(RetrieveAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]


class PatientUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]
