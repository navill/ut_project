from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from accounts.api import serializers
from accounts.api.permissions import OnlyOwner, OwnerUpdateOrReadDoctor, IsDoctor
from accounts.models import Doctor, Patient


# [POST] /doctors/create
class DoctorSignUpAPIView(CreateAPIView):
    serializer_class = serializers.DoctorSignUpSerializer
    permission_classes = [AllowAny]
    lookup_field = 'pk'


# [GET] /doctors
class DoctorListAPIView(ListAPIView):
    queryset = Doctor.objects.all().order_by('-user__date_joined')
    serializer_class = serializers.RelatedDoctorSerializer
    permission_classes = [IsDoctor]
    # renderer_classes = [JSONRenderer]
    lookup_field = 'pk'


# [GET, PUT] /doctors/<slug>
class DoctorDetailUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Doctor.objects.all()
    serializer_class = serializers.DoctorSerializer
    permission_classes = [OnlyOwner]  # +owner
    lookup_field = 'pk'


# [POST] /patients/create
class PatientSignUpAPIView(CreateAPIView):
    serializer_class = serializers.PatientSignUpSerializer
    permission_classes = [AllowAny]
    lookup_field = 'pk'


# [GET] /patients
class PatientListAPIView(ListAPIView):
    queryset = Patient.objects.all().order_by('-user__date_joined')
    serializer_class = serializers.SimpleRelatedPatientSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = ['pk']


# [GET, PUT] /patients/<slug>
class PatientDetailUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Patient.objects.all()
    serializer_class = serializers.PatientSerailizer
    permission_classes = [OwnerUpdateOrReadDoctor]  # +owner
    lookup_field = 'pk'
