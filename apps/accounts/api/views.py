from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
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
    serializer_class = AccountsTokenRefreshSerializer
    # TokenRefreshView 상속받을 때 반드시 authentication_classes 추가(default authentication 적용 안됨)
    authentication_classes = [CustomJWTTokenUserAuthentication]
    permission_classes = [IsAuthenticated]


class TokenLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            self._logout_using_refresh_token(request)
        except (ValueError, TokenError) as e:
            raise e
        return Response(status=status.HTTP_205_RESET_CONTENT)

    def _logout_using_refresh_token(self, request):
        user = request.user
        refresh_token = request.data.get('refresh', None)
        if refresh_token:
            refresh = RefreshToken(refresh_token)
            refresh.blacklist()
        else:
            raise ValueError("you don't have refresh token")
        user.set_token_expired(0)


class DoctorSignUpAPIView(CreateAPIView):
    queryset = Doctor.objects.select_all()
    serializer_class = serializers.DoctorSignUpSerializer
    permission_classes = [AllowAny]


class DoctorListAPIView(ListAPIView):
    queryset = Doctor.objects.select_all().defer_fields().order_by('-created_at')
    serializer_class = serializers.DoctorListSerializer
    permission_classes = [IsDoctor]


class DoctorRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Doctor.objects.select_all()
    serializer_class = serializers.DoctorRetrieveSerializer
    permission_classes = [IsOwner]
    lookup_field = 'pk'


class PatientSignUpAPIView(CreateAPIView):
    queryset = Patient.objects.select_all()
    serializer_class = serializers.PatientSignUpSerializer
    permission_classes = [AllowAny]
    lookup_field = 'pk'


class PatientListAPIView(ListAPIView):
    queryset = Patient.objects.select_all().defer_fields().order_by('-created_at')
    serializer_class = serializers.PatientListSerailizer
    permission_classes = [IsDoctor]
    lookup_field = 'pk'

    def get_queryset(self):
        queryset = super().get_queryset()
        doctor = self.request.user.doctor
        return queryset.filter(doctor=doctor)


class PatientRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Patient.objects.select_all()
    serializer_class = serializers.PatientRetrieveSerializer
    permission_classes = [CareDoctorReadOnly | IsOwner]
    lookup_field = 'pk'
