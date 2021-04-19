from typing import TYPE_CHECKING, Union

from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.response import Response

from accounts.api.permissions import IsDoctor, IsPatient, IsOwner, CareDoctorReadOnly
from files import docs
from files.api.mixins import CommonUploaderCheckMixin
from files.api.serializers import (PatientFileUploadSerializer,
                                   DoctorFileUploadSerializer,
                                   DoctorFileListSerializer,
                                   PatientFileListSerializer,
                                   DoctorFlieRetrieveSerializer,
                                   PatientFlieRetrieveSerializer,
                                   PatientFlieUpdateSerializer,
                                   DoctorFileDownloadSerializer,
                                   PatientFileDownloadSerializer)
from files.api.utils import Downloader
from files.models import DoctorFile, PatientFile

if TYPE_CHECKING:
    from django.http import FileResponse


class DoctorFileListAPIView(CommonUploaderCheckMixin, ListAPIView):
    queryset = DoctorFile.objects.select_all()
    permission_classes = [IsDoctor]
    serializer_class = DoctorFileListSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return DoctorFile.objects.none()
        queryset = self.filter_with_uploader(self.request.user, super().get_queryset())
        return queryset

    @swagger_auto_schema(**docs.doctor_file_list)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class DoctorFileRetrieveAPIView(RetrieveAPIView):
    queryset = DoctorFile.objects.select_all()
    permission_classes = [IsOwner]
    serializer_class = DoctorFlieRetrieveSerializer
    lookup_field = 'id'

    @swagger_auto_schema(**docs.doctor_file_detail)
    def get(self, request, *args, **kwargs):
        return super(DoctorFileRetrieveAPIView, self).get(request, *args, **kwargs)


class DoctorFileUpdateAPIView(UpdateAPIView):
    queryset = DoctorFile.objects.select_all()
    permission_classes = [IsOwner]
    serializer_class = DoctorFlieRetrieveSerializer
    lookup_field = 'id'

    @swagger_auto_schema(**docs.doctor_file_update)
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @swagger_auto_schema(**docs.doctor_file_update, deprecated=True)
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class DoctorFileUploadAPIView(CreateAPIView):
    queryset = DoctorFile.objects.select_all()
    permission_classes = [IsDoctor]
    serializer_class = DoctorFileUploadSerializer

    @swagger_auto_schema(**docs.doctor_file_create)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class PatientFileListAPIView(CommonUploaderCheckMixin, ListAPIView):
    queryset = PatientFile.objects.select_all()
    permission_classes = [IsPatient]
    serializer_class = PatientFileListSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return PatientFile.objects.none()
        queryset = self.filter_with_uploader(self.request.user, super().get_queryset())
        return queryset

    @swagger_auto_schema(**docs.patient_file_list)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class PatientFileRetrieveAPIView(RetrieveAPIView):
    queryset = PatientFile.objects.select_all()
    permission_classes = [IsOwner | CareDoctorReadOnly]
    serializer_class = PatientFlieRetrieveSerializer
    lookup_field = 'id'

    @swagger_auto_schema(**docs.patient_file_detail)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class PatientFileUpdateAPIView(UpdateAPIView):
    queryset = PatientFile.objects.select_all()
    permission_classes = [IsOwner]
    serializer_class = PatientFlieUpdateSerializer
    lookup_field = 'id'

    @swagger_auto_schema(**docs.patient_file_update)
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @swagger_auto_schema(**docs.patient_file_update, deprecated=True)
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class PatientFileUploadAPIView(CreateAPIView):
    queryset = PatientFile.objects.select_all()
    permission_classes = [IsPatient]
    serializer_class = PatientFileUploadSerializer

    @swagger_auto_schema(**docs.patient_file_create)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class DoctorFileDownloadAPIView(RetrieveAPIView):
    queryset = DoctorFile.objects.all()
    permission_classes = [IsOwner]
    serializer_class = DoctorFileDownloadSerializer
    lookup_field = 'id'

    @swagger_auto_schema(operation_summary="의사 파일 다운로드")
    def get(self, request, *args, **kwargs) -> Union['FileResponse', 'Response']:
        file_object = self.get_object()
        if file_object.deleted:
            return Response({"error": "this file was deleted"})
        downloader = Downloader(instance=file_object)
        return downloader.response()


class PatientFileDownloadAPIView(RetrieveAPIView):
    queryset = PatientFile.objects.all()
    permission_classes = [IsOwner | CareDoctorReadOnly]
    serializer_class = PatientFileDownloadSerializer
    lookup_field = 'id'

    @swagger_auto_schema(operation_summary="환자 파일 다운로드")
    def get(self, request, *args, **kwargs) -> 'FileResponse':
        file_object = self.get_object()
        downloader = Downloader(instance=file_object)
        return downloader.response()
