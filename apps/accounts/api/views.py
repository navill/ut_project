from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import AllowAny

from accounts.api.serializers import StaffSignUpSerializer


class StaffSignUpAPIView(CreateAPIView):
    serializer_class = StaffSignUpSerializer
    permission_classes = [AllowAny]


class StaffListAPIView(ListAPIView):
    queryset = None
    serializer_class = StaffSignUpSerializer
    permission_classes = [AllowAny]


class NormalSignUpView(CreateAPIView):
    queryset = None
    serializer_class = StaffSignUpSerializer
    permission_classes = [AllowAny]


class NormalListAPIView(ListAPIView):
    serializer_class = StaffSignUpSerializer
    permission_classes = [AllowAny]
