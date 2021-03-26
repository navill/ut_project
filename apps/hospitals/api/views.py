from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny

from accounts.api.permissions import IsSuperUser
from config.utils.doc_utils import CommonFilterDescriptionInspector
from hospitals import docs
from hospitals.api import serializers
from hospitals.api.filters import DepartmentFilter, MajorFilter, MedicalCenterFilter
from hospitals.api.serializers import (DepartmentListSerializer,
                                       DepartmentCreateSerializer,
                                       DepartmentRetreiveSerializer,
                                       DepartmentUpdateSerializer,
                                       MajorListSerializer,
                                       MajorCreateSerializer,
                                       MajorRetrieveSerializer,
                                       MajorUpdateSerializer)
from hospitals.models import MedicalCenter, Department, Major

"""
Choice list
"""


class MedicalCenterChoiceAPIView(ListAPIView):
    queryset = MedicalCenter.objects.choice_fields()
    serializer_class = serializers.MedicalCenterChoiceSerializer
    permission_classes = [AllowAny]
    filter_class = MedicalCenterFilter

    @swagger_auto_schema(**docs.medical_center_choice, filter_inspectors=[CommonFilterDescriptionInspector])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class DepartmentChoiceAPIView(ListAPIView):
    queryset = Department.objects.choice_fields()
    serializer_class = serializers.DepartmentChoiceSerializer
    permission_classes = [AllowAny]
    filter_class = DepartmentFilter

    @swagger_auto_schema(**docs.department_choice, filter_inspectors=[CommonFilterDescriptionInspector])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class MajorChoiceAPIView(ListAPIView):
    queryset = Major.objects.choice_fields()
    serializer_class = serializers.MajorChoiceSerializer
    permission_classes = [AllowAny]
    filter_class = MajorFilter

    @swagger_auto_schema(**docs.major_choice, filter_inspectors=[CommonFilterDescriptionInspector])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class DepartmentNestedChildList(ListAPIView):
    queryset = Department.objects.prefetch_all()
    serializer_class = serializers.DepartmentNestedMajor
    permission_classes = [AllowAny]


"""
MedicalCenter CRUDL View
"""


class MedicalCenterListAPIView(ListAPIView):
    queryset = MedicalCenter.objects.all()
    serializer_class = serializers.MedicalCenterListSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(**docs.medical_center_list)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class MedicalCenterCreateAPIView(CreateAPIView):
    serializer_class = serializers.MedicalCenterCreateSerializer
    permission_classes = [IsSuperUser]

    @swagger_auto_schema(**docs.medical_center_create)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class MedicalCenterRetrieveAPIView(RetrieveAPIView):
    queryset = MedicalCenter.objects.all()
    serializer_class = serializers.MedicalCenterRetrieveSerializer
    permission_classes = [IsSuperUser]
    lookup_field = 'pk'

    @swagger_auto_schema(**docs.medical_center_detail)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class MedicalCenterUpdateAPIView(UpdateAPIView):
    queryset = MedicalCenter.objects.all()
    serializer_class = serializers.MedicalCenterUpdateSerializer
    permission_classes = [IsSuperUser]
    lookup_field = 'pk'

    @swagger_auto_schema(**docs.medical_center_update)
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary='병원 정보 수정', deprecated=True)
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


"""
Department CRUDL view
"""


class DepartmentListAPIView(ListAPIView):
    queryset = Department.objects.select_all()
    serializer_class = DepartmentListSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(**docs.department_list)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class DepartmentCreateAPIView(CreateAPIView):
    serializer_class = DepartmentCreateSerializer
    permission_classes = [IsSuperUser]

    @swagger_auto_schema(**docs.department_create)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class DepartmentRetrieveAPIView(RetrieveAPIView):
    queryset = Department.objects.select_all()
    serializer_class = DepartmentRetreiveSerializer
    permission_classes = [IsSuperUser]

    @swagger_auto_schema(**docs.department_detail)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class DepartmentUpdateAPIView(UpdateAPIView):
    queryset = Department.objects.select_all()
    serializer_class = DepartmentUpdateSerializer
    permission_classes = [IsSuperUser]
    lookup_field = 'pk'

    @swagger_auto_schema(**docs.department_update)
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary='부서 정보 수정', deprecated=True)
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


"""
Major CRUDL view
"""


class MajorListAPIView(ListAPIView):
    queryset = Major.objects.select_all()
    serializer_class = MajorListSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(**docs.major_list)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class MajorCreateAPIView(CreateAPIView):
    serializer_class = MajorCreateSerializer
    permission_classes = [IsSuperUser]

    @swagger_auto_schema(**docs.major_create)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class MajorRetrieveAPIView(RetrieveAPIView):
    queryset = Major.objects.select_all()
    serializer_class = MajorRetrieveSerializer
    permission_classes = [IsSuperUser]
    lookup_field = 'pk'

    @swagger_auto_schema(**docs.major_detail)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class MajorUpdateAPIView(UpdateAPIView):
    queryset = Major.objects.select_all()
    serializer_class = MajorUpdateSerializer
    permission_classes = [IsSuperUser]
    lookup_field = 'pk'

    @swagger_auto_schema(**docs.major_update)
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary='전공 정보 수정', deprecated=True)
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
