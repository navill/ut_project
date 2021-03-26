from typing import Type, NoReturn

from django.db.models import QuerySet
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts import docs
from accounts.api import serializers
from accounts.api.authentications import CustomJWTTokenUserAuthentication
from accounts.api.filters import DoctorFilter, PatientFilter
from accounts.api.permissions import IsDoctor, IsOwner, CareDoctorReadOnly, RelatedPatientReadOnly
from accounts.api.serializers import AccountsTokenSerializer, AccountsTokenRefreshSerializer, DoctorSignUpSerializer
from accounts.models import Doctor, Patient
from config.utils.doc_utils import CommonFilterDescriptionInspector


class AccountsTokenPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = AccountsTokenSerializer

    @swagger_auto_schema(**docs.login_with_token)
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class AccountsTokenRefreshView(TokenRefreshView):
    serializer_class = AccountsTokenRefreshSerializer
    authentication_classes = [CustomJWTTokenUserAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(**docs.refresh_token)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class TokenLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(**docs.destroy_token)
    def post(self, request, *args, **kwargs):
        try:
            self._logout_using_refresh_token(request)
        except (ValueError, TokenError) as e:
            raise e
        return Response(status=status.HTTP_205_RESET_CONTENT)

    def _logout_using_refresh_token(self, request: Request) -> NoReturn:
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
    permission_classes = [AllowAny]

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
        return self.partial_update(request, *args, **kwargs)

    @swagger_auto_schema(**docs.doctor_update, deprecated=True)
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
        if getattr(self, 'swagger_fake_view', False):
            return Patient.objects.none()

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
        return self.partial_update(request, *args, **kwargs)

    @swagger_auto_schema(**docs.patient_update, deprecated=True)
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class DoctorChoicesAPIView(ListAPIView):
    queryset = Doctor.objects.choice_fields()
    serializer_class = serializers.DoctorChoiceSerializer
    permission_classes = [AllowAny]
    filter_class = DoctorFilter

    @swagger_auto_schema(**docs.doctor_choice, filter_inspectors=[CommonFilterDescriptionInspector])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class PatientChoicesAPIView(ListAPIView):
    queryset = Patient.objects.choice_fields()
    serializer_class = serializers.PatientChoiceSerializer
    permission_classes = [AllowAny]
    filter_class = PatientFilter

    @swagger_auto_schema(**docs.patient_choice, filter_inspectors=[CommonFilterDescriptionInspector])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
