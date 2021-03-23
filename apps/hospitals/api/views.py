from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.permissions import AllowAny

from hospitals.api import serializers
from hospitals.models import MedicalCenter, Department, Major

"""
Choice list
"""


class MedicalCenterChoiceAPIView(generics.ListAPIView):
    """
    테스트 - 병원 정보(병원, 부서, 전공)

    ---
    - 특정 병원의 모든 전공 및 부서 리스트

    """
    queryset = MedicalCenter.objects.choice_fields()
    serializer_class = serializers.MedicalCenterChoiceSerializer
    permission_classes = [AllowAny]
    filterset_fields = ['id', 'name']


class DepartmentChoiceAPIView(generics.ListAPIView):
    queryset = Department.objects.choice_fields()
    serializer_class = serializers.DepartmentChoiceSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['medical_center_id', 'name']


class MajorChoiceAPIView(generics.ListAPIView):
    queryset = Major.objects.choice_fields()
    serializer_class = serializers.MajorChoiceSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['department_id', 'name']


class DepartmentNestedChildList(generics.ListAPIView):
    """
    테스트 - 부서 정보(부서, 전공)

    ---

    """
    queryset = Department.objects.prefetch_all()
    serializer_class = serializers.DepartmentNestedMajor
    permission_classes = [AllowAny]


"""
MedicalCenter CRUDL View
"""


class MedicalCenterListAPIView(generics.ListAPIView):
    """
    병원 리스트

    ---
    ## 등록된 병원의 리스트 출력
    """
    queryset = MedicalCenter.objects.all()
    serializer_class = serializers.MedicalCenterListSerializer
    permission_classes = [AllowAny]


class MedicalCenterCreateAPIView(generics.CreateAPIView):
    """
    병원 객체 생성

    ---
    ## 병원 정보를 등록
    """
    serializer_class = serializers.MedicalCenterCreateSerializer
    permission_classes = [AllowAny]  # IsSuperuser


class MedicalCenterRetrieveAPIView(generics.RetrieveAPIView):
    """
    병원 정보(Detail) 접근

    ---
    ## 병원 상세 정보에 접근
    """
    queryset = MedicalCenter.objects.all()
    serializer_class = serializers.MedicalCenterRetrieveSerializer
    permission_classes = [AllowAny]  # IsSuperuser


class MedicalCenterUpdateAPIView(generics.UpdateAPIView):
    """
    병원 정보 수정

    ---
    ## 병원 상세 정보를 수정
    """
    queryset = MedicalCenter.objects.all()
    serializer_class = serializers.MedicalCenterRetrieveSerializer
    permission_classes = [AllowAny]  # IsSuperuser


"""
Department CRUDL view
"""


class DepartmentListAPIView(generics.ListAPIView):
    """
    부서 리스트

    ---
    ## 등록된 부서의 리스트 출력
    """
    queryset = Department.objects.select_all()
    serializer_class = serializers.DepartmentListSerializer
    permission_classes = [AllowAny]


class DepartmentCreateAPIView(generics.CreateAPIView):
    """
    부서 객체 생성

    ---
    ## 병원의 부서 정보를 등록
    """
    serializer_class = serializers.DepartmentCreateSerializer
    permission_classes = [AllowAny]  # IsSuperuser


class DepartmentRetrieveAPIView(generics.RetrieveAPIView):
    """
    부서 세부 정보(detail) 접근

    ---
    ## 부서의 세부 정보에 접근

    """
    queryset = Department.objects.select_all()
    serializer_class = serializers.DepartmentRetreiveSerializer
    permission_classes = [AllowAny]  # IsSuperuser


class DepartmentUpdateAPIView(generics.UpdateAPIView):
    """
    부서 정보 수정

    ---
    ## 부서의 세부 정보 수정
    """
    queryset = Department.objects.select_all()
    serializer_class = serializers.DepartmentRetreiveSerializer
    permission_classes = [AllowAny]  # IsSuperuser


"""
Major CRUDL view
"""


class MajorListAPIView(generics.ListAPIView):
    """
    전공 리스트

    ---
    ## 병원의 부서에 포함된 전공 리스트 출력
    """
    queryset = Major.objects.select_all()
    serializer_class = serializers.MajorListSerializer
    permission_classes = [AllowAny]


class MajorCreateAPIView(generics.CreateAPIView):
    """
    전공 객체 생성

    ---
    ## 전공 정보 등록
    """
    serializer_class = serializers.MajorCreateSerializer
    permission_classes = [AllowAny]  # IsSuperuser


class MajorRetrieveAPIView(generics.RetrieveAPIView):
    """
    전공 세부 정보 접근

    ---
    ## 전공의 세부 정보에 접근
    """
    queryset = Major.objects.select_all()
    serializer_class = serializers.MajorRetrieveSerializer
    permission_classes = [AllowAny]  # IsSuperuser


class MajorUpdateAPIView(generics.UpdateAPIView):
    """
    전공 정보 수정

    ---
    ## 전공의 세부 정보 수정
    """
    queryset = Major.objects.select_all()
    serializer_class = serializers.MajorRetrieveSerializer
    permission_classes = [AllowAny]  # IsSuperuser
