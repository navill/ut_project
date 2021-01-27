import json
from typing import Type

from django.db.models import QuerySet
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
from accounts.api.permissions import IsDoctor, IsOwner, CareDoctorReadOnly, IsSuperUser
from accounts.api.serializers import AccountsTokenSerializer, AccountsTokenRefreshSerializer, DoctorSignUpSerializer
from accounts.models import Doctor, Patient, Gender
from hospitals.models import Major


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
    """
    {
    "major": "select 'id'"
    }
    """
    queryset = Doctor.objects.select_all()
    serializer_class = DoctorSignUpSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        doc_values = self.__doc__
        default_values = json.loads(doc_values)
        major = Major.objects.related_all().values('id', 'department__medical_center__name', 'department', 'name')
        default_values['gender'] = Gender.choices
        default_values['major'] = major
        return Response(default_values)


class DoctorListAPIView(ListAPIView):
    queryset = Doctor.objects.related_all().order_by('-created_at')
    serializer_class = serializers.DoctorListSerializer
    permission_classes = [IsSuperUser | IsDoctor]


class DoctorRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Doctor.objects.select_all()
    serializer_class = serializers.DoctorRetrieveSerializer
    permission_classes = [IsOwner]
    lookup_field = 'pk'


class PatientSignUpAPIView(CreateAPIView):
    """
    {
        "doctors": "select 'user_id'"
    }
    """
    queryset = Patient.objects.select_all()
    serializer_class = serializers.PatientSignUpSerializer
    permission_classes = [AllowAny]
    lookup_field = 'pk'

    def get(self, request, *args, **kwargs):
        doc_values = self.__doc__
        default_values = json.loads(doc_values)
        doctors = Doctor.objects.all().values('user_id', 'full_name', 'major__name')
        default_values['gender'] = Gender.choices
        default_values['doctor'] = doctors
        return Response(default_values)


class PatientListAPIView(ListAPIView):
    queryset = Patient.objects.select_all().defer_option_fields().order_by('-created_at')
    serializer_class = serializers.PatientListSerailizer
    permission_classes = [IsDoctor]
    lookup_field = 'pk'

    def get_queryset(self) -> Type[QuerySet]:
        queryset = super().get_queryset()
        doctor = self.request.user.doctor
        return queryset.filter(doctor=doctor)


class PatientRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Patient.objects.select_all()
    serializer_class = serializers.PatientRetrieveSerializer
    permission_classes = [CareDoctorReadOnly | IsOwner]
    lookup_field = 'pk'
