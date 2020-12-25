from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.api import serializers
from accounts.api.authentications import CustomJWTTokenUserAuthentication
from accounts.api.permissions import IsDoctor, IsOwner, CareDoctorReadOnly
from accounts.api.serializers import AccountsTokenSerializer, AccountsTokenRefreshSerializer
from accounts.models import Doctor, Patient


class AccountsTokenPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = AccountsTokenSerializer


class AccountsTokenRefreshView(TokenRefreshView):
    permission_classes = [IsAuthenticated]
    serializer_class = AccountsTokenRefreshSerializer


class TokenLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        refresh_token = request.data.get('refresh')
        refresh = RefreshToken(refresh_token)
        refresh.blacklist()
        user.set_token_expired(0)
        return Response(status=status.HTTP_205_RESET_CONTENT)


# [POST] /doctors/create
class DoctorSignUpAPIView(CreateAPIView):
    serializer_class = serializers.DoctorSignUpSerializer
    authentication_classes = []

    permission_classes = [AllowAny]
    lookup_field = 'pk'

    def post(self, request, *args, **kwargs):
        print(args)
        print(kwargs)
        print(request)
        print(request.data)
        return super().post(request, *args, **kwargs)


# [GET] /doctors
class DoctorListAPIView(ListAPIView):
    queryset = Doctor.objects.all().ordered()
    serializer_class = serializers.DoctorSerializer
    authentication_classes = [CustomJWTTokenUserAuthentication]
    permission_classes = [IsDoctor]
    lookup_field = 'pk'


# [GET, PUT] /doctors/<pk>
class DoctorRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Doctor.objects.all()
    serializer_class = serializers.DoctorSerializer
    authentication_classes = [CustomJWTTokenUserAuthentication]
    permission_classes = [IsOwner]
    lookup_field = 'pk'


# [POST] /patients/create
class PatientSignUpAPIView(CreateAPIView):
    serializer_class = serializers.PatientSignUpSerializer
    authentication_classes = []
    permission_classes = [AllowAny]
    lookup_field = 'pk'


# [GET] /patients
class PatientListAPIView(ListAPIView):
    queryset = Patient.objects.all().ordered()
    serializer_class = serializers.PatientSerailizer
    authentication_classes = [CustomJWTTokenUserAuthentication]
    permission_classes = [IsDoctor]
    lookup_field = 'pk'

    def get_queryset(self):
        queryset = super().get_queryset()
        doctor = self.request.user.doctor  # user.doctor는 permissions_class에서 확정되므로 에러검사 하지 않음
        return queryset.filter(user_doctor=doctor)


# [GET, PUT] /patients/<pk>
class PatientRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Patient.objects.all()
    serializer_class = serializers.PatientSerailizer
    authentication_classes = [CustomJWTTokenUserAuthentication]
    permission_classes = [CareDoctorReadOnly | IsOwner]
    lookup_field = 'pk'
