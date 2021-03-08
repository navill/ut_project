from typing import Type

from django.db.models import QuerySet
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts import docs
from accounts.api import serializers
from accounts.api.authentications import CustomJWTTokenUserAuthentication
from accounts.api.permissions import IsDoctor, IsOwner, CareDoctorReadOnly, IsSuperUser, RelatedPatientReadOnly
from accounts.api.serializers import AccountsTokenSerializer, AccountsTokenRefreshSerializer, DoctorSignUpSerializer
from accounts.models import Doctor, Patient


class AccountsTokenPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = AccountsTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


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
    serializer_class = DoctorSignUpSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(**docs.doctor_signup)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class DoctorListAPIView(ListAPIView):
    queryset = Doctor.objects.select_all().order_by('-created_at')
    serializer_class = serializers.DoctorListSerializer
    permission_classes = [IsSuperUser | IsDoctor]

    @swagger_auto_schema(**docs.doctor_list)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class DoctorRetrieveAPIView(RetrieveAPIView):
    queryset = Doctor.objects.select_all()
    serializer_class = serializers.DoctorDetailSerializer
    permission_classes = [IsOwner | RelatedPatientReadOnly]
    lookup_field = 'pk'

    @swagger_auto_schema(**docs.doctor_detail)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class DoctorUpdateAPIView(UpdateAPIView):
    queryset = Doctor.objects.select_all()
    serializer_class = serializers.DoctorUpdateSerializer
    permission_classes = [IsOwner]
    lookup_field = 'pk'

    @swagger_auto_schema(**docs.doctor_update)
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(**docs.doctor_update)
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class PatientSignUpAPIView(CreateAPIView):
    queryset = Patient.objects.select_all()
    serializer_class = serializers.PatientSignUpSerializer
    permission_classes = [AllowAny]
    lookup_field = 'pk'

    @swagger_auto_schema(**docs.patient_signup)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class PatientListAPIView(ListAPIView):
    queryset = Patient.objects.select_all().order_by('-created_at')
    serializer_class = serializers.PatientListSerializer
    permission_classes = [IsDoctor]
    lookup_field = 'pk'

    def get_queryset(self) -> Type[QuerySet]:
        queryset = super().get_queryset()
        doctor = self.request.user.doctor
        return queryset.filter(doctor=doctor)

    @swagger_auto_schema(**docs.patient_list)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class PatientRetrieveAPIView(RetrieveAPIView):
    queryset = Patient.objects.select_all()
    serializer_class = serializers.PatientDetailSerializer
    permission_classes = [CareDoctorReadOnly | IsOwner]
    lookup_field = 'pk'

    @swagger_auto_schema(**docs.patient_detail)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class PatientUpdateAPIView(UpdateAPIView):
    queryset = Patient.objects.select_all()
    serializer_class = serializers.PatientUpdateSerializer
    permission_classes = [IsOwner]
    lookup_field = 'pk'

    @swagger_auto_schema(**docs.patient_update)
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(**docs.patient_update)
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
