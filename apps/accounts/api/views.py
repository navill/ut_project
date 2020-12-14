from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from accounts.api.permissions import OnlyDoctor
from accounts.api.serializers import DoctorSignUpSerializer, PatientSignUpSerializer, DoctorSerializer, \
    PatientSerializer
from accounts.models import Doctor, Patient


# [POST] /doctors/create
class DoctorSignUpAPIView(CreateAPIView):
    serializer_class = DoctorSignUpSerializer
    permission_classes = [AllowAny]


# [GET] /doctors
class DoctorListAPIView(ListAPIView):
    queryset = Doctor.objects.all().order_by('-user__date_joined')
    serializer_class = DoctorSerializer
    permission_classes = [OnlyDoctor]


# [GET, PUT] /doctors/<slug>
class DoctorDetailUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [OnlyDoctor]  # +owner


# [POST] /patients/create
class PatientSignUpAPIView(CreateAPIView):
    serializer_class = PatientSignUpSerializer
    permission_classes = [AllowAny]


# [GET] /patients
class PatientListAPIView(ListAPIView):
    queryset = Patient.objects.all().order_by('-user__date_joined')
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]


# [GET, PUT] /patients/<slug>
class PatientDetailUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]  # +owner
