from typing import Type

from django.db.models import QuerySet
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.api import serializers
from accounts.api.authentications import CustomJWTTokenUserAuthentication
from accounts.api.permissions import IsDoctor, IsOwner, CareDoctorReadOnly, IsSuperUser
from accounts.api.serializers import AccountsTokenSerializer, AccountsTokenRefreshSerializer, DoctorSignUpSerializer
from accounts.models import Doctor, Patient
from config.utils.api_utils import InputValueSupporter


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
    """
    [CREATE] 의사 계정 생성

    ---
    ## 의사 계정 생성
    - permissions: Any
    - result: 생성된 객체 정보 출력
    """
    queryset = Doctor.objects.select_all()
    serializer_class = DoctorSignUpSerializer
    permission_classes = [AllowAny]
    # fields_to_display = 'gender', 'major'


class DoctorListAPIView(ListAPIView):
    """
    [LIST] 의사 정보

    ---
    ## 등록된 의사의 리스트 출력
    - permissions: 관리자 계정
    - result: 의사 객체들 출력
    """
    queryset = Doctor.objects.select_all().order_by('-created_at')
    serializer_class = serializers.DoctorListSerializer
    permission_classes = [IsSuperUser | IsDoctor]


class DoctorRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    """
    [DETAIL, UPDATE] 의사 정보

    ---
    ## 등록된 의사의 세부 정보 및 수정
    - permissions: 객체 소유자
    - result(detail): 의사 세부 정보
    - result(update): 수정 사항이 반영된 의사의 세부정보

    """
    queryset = Doctor.objects.select_all()
    serializer_class = serializers.DoctorDetailSerializer
    permission_classes = [IsOwner]
    lookup_field = 'pk'


class PatientSignUpAPIView(CreateAPIView):
    """
    [CREATE] 환자 계정 생성

    ---
    ## 환자 계정 생성
    - permissions: Any
    - result: 생성된 객체 정보 출력
    """
    queryset = Patient.objects.select_all()
    serializer_class = serializers.PatientSignUpSerializer
    permission_classes = [AllowAny]
    lookup_field = 'pk'

    @swagger_auto_schema(request_body=serializers.PatientSignUpSerializer)
    def post(self, request, *args, **kwargs):
        return super(PatientSignUpAPIView, self).post(request, *args, **kwargs)


class PatientListAPIView(ListAPIView):
    """
    [LIST] 환자 정보

    ---
    ## 등록된 환자의 리스트 정보
    - premissions: 의사 계정 접근 가능
    - result: 로그인한 의사의 담당 환자 리스트 출력
    """
    queryset = Patient.objects.select_all().order_by('-created_at')
    serializer_class = serializers.PatientListSerializer
    permission_classes = [IsDoctor]
    lookup_field = 'pk'

    def get_queryset(self) -> Type[QuerySet]:
        queryset = super().get_queryset()
        doctor = self.request.user.doctor
        return queryset.filter(doctor=doctor)


class PatientRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    """
    [DETAIL, UPDATE] 환자 정보

    ---
    ## 등록된 환자의 세부 정보
    - permissions: 환자 본인 계정(읽기 및 수정), 환자를 담당하는 의사 계정(읽기 전용)
    - result(detail): 환자의 세부 정보 출력
    - result(update): 수정사항이 반영된 환자의 세부 정보 출력

    """
    queryset = Patient.objects.select_all()
    serializer_class = serializers.PatientDetailSerializer
    permission_classes = [CareDoctorReadOnly | IsOwner]
    lookup_field = 'pk'
