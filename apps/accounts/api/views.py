from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny

from accounts.api import serializers
from accounts.api.permissions import IsDoctor, IsOwner, DoctorReadOnly
from accounts.models import Doctor, Patient


# [POST] /doctors/create
class DoctorSignUpAPIView(CreateAPIView):
    serializer_class = serializers.DoctorSignUpSerializer
    permission_classes = [AllowAny]
    lookup_field = 'pk'


# [GET] /doctors
class DoctorListAPIView(ListAPIView):
    queryset = Doctor.objects.all().order_by('-user__date_joined')
    serializer_class = serializers.DoctorSerializer
    permission_classes = [IsDoctor]  # product에서는 IsDoctor -> IsSuperUser로 변경
    # renderer_classes = [JSONRenderer]
    lookup_field = 'pk'


# [GET, PUT] /doctors/<pk>
class DoctorDetailUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Doctor.objects.all()
    serializer_class = serializers.DoctorSerializer
    permission_classes = [IsOwner]  # +owner
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
    permission_classes = [IsDoctor]  # product에서는 IsDoctor -> IsSuperUser로 변경
    lookup_field = ['pk']

    def get_queryset(self):
        queryset = super().get_queryset()
        doctor = self.request.user.doctor  # user.doctor는 permissions_class에서 확정되므로 에러 구문 없이 진행
        return queryset.filter(user_doctor=doctor)


# [GET, PUT] /patients/<pk>
class PatientDetailUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Patient.objects.all()
    serializer_class = serializers.PatientSerailizer
    permission_classes = [DoctorReadOnly | IsOwner]
    lookup_field = 'pk'
