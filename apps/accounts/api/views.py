from typing import Type, NoReturn, Dict, Any, Optional

from django.db.models import QuerySet
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
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
    def post(self, request, *args, **kwargs) -> Response:
        serialized_data = self.get_serializer_data(request_data=request.data)
        refresh_token = self.get_refresh_token_from(serialized_data)
        response = self.create_response(serialized_data, refresh_token)
        return response

    def get_refresh_token_from(self, data: Dict[str, Any]) -> Optional[str]:
        return data.pop('refresh', None)

    def get_serializer_data(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        serializer = self.get_serializer(data=request_data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            raise ValidationError(detail=e)
        return serializer.validated_data

    def create_response(self, serialized_data, refresh_token):
        if refresh_token:
            response_data, response_status = serialized_data, status.HTTP_200_OK
        else:
            response_data, response_status = {'error': 'can not create refresh token'}, status.HTTP_400_BAD_REQUEST

        response = Response(data=response_data, status=response_status)
        response.set_cookie(key='refresh_token', value=refresh_token, httponly=True)  # ssl 적용시 secure=True
        return response


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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]
    filter_class = DoctorFilter

    @swagger_auto_schema(**docs.doctor_choice)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class PatientChoicesAPIView(ListAPIView):
    queryset = Patient.objects.choice_fields()
    serializer_class = serializers.PatientChoiceSerializer
    permission_classes = [IsAuthenticated]
    filter_class = PatientFilter

    @swagger_auto_schema(**docs.patient_choice, filter_inspectors=[CommonFilterDescriptionInspector])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@api_view(['GET'])
@permission_classes([AllowAny])
def session_logout_view(request):
    request.session.flush()
    request.user.user_type = None
    data = {'success': 'Sucessfully logged out'}
    return Response(data=data, status=status.HTTP_200_OK)
