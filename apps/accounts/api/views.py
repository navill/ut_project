from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from accounts.api.serializers import DoctorSignUpSerializer, PatientSignUpSerializer
from accounts.models import Doctor, Patient


class DoctorSignUpAPIView(CreateAPIView):
    serializer_class = DoctorSignUpSerializer
    permission_classes = [AllowAny]


class DoctorListAPIView(ListAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSignUpSerializer
    permission_classes = [IsAuthenticated]
    

class PatientSignUpAPIView(CreateAPIView):
    serializer_class = PatientSignUpSerializer
    permission_classes = [AllowAny]


class PatientListAPIView(ListAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSignUpSerializer
    permission_classes = [IsAuthenticated]
