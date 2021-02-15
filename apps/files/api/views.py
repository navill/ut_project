from typing import Type

from django.db.models import QuerySet
from django.http import FileResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, RetrieveUpdateAPIView
from rest_framework.parsers import FileUploadParser

from accounts.api.permissions import IsDoctor, IsPatient, IsOwner
from config.utils.api_utils import InputValueSupporter
from files.api.mixins import QuerySetMixin
from files.api.serializers import (PatientFileUploadSerializer,
                                   DoctorFileUploadSerializer,
                                   DoctorFileListSerializer,
                                   PatientFileListSerializer,
                                   PatientUploadedFileListSerializer,
                                   DoctorUploadedFileListSerializer,
                                   DoctorFlieRetrieveSerializer,
                                   DoctorUploadedFileRetrieveSerializer,
                                   PatientFlieRetrieveSerializer,
                                   DoctorFileDownloadSerializer,
                                   PatientFileDownloadSerializer)
from files.api.utils import Downloader
from files.models import DoctorFile, PatientFile


class DoctorFileListAPIView(QuerySetMixin, ListAPIView):
    queryset = DoctorFile.objects.select_all()
    permission_classes = [IsDoctor]
    serializer_class = DoctorFileListSerializer


class DoctorFileRetrieveAPIView(RetrieveUpdateAPIView):
    queryset = DoctorFile.objects.select_all()
    permission_classes = [IsOwner | IsDoctor]
    serializer_class = DoctorFlieRetrieveSerializer
    lookup_field = 'id'


class DoctorFileUploadAPIView(InputValueSupporter, CreateAPIView):
    queryset = DoctorFile.objects.select_all()
    permission_classes = [IsDoctor]
    serializer_class = DoctorFileUploadSerializer
    parser_classes = (FileUploadParser,)

    fields_to_display = 'prescription'


class DoctorUploadedFileListAPIView(ListAPIView):
    queryset = DoctorFile.objects.select_all()
    permission_classes = [IsDoctor]
    serializer_class = DoctorUploadedFileListSerializer

    def get_queryset(self) -> Type[QuerySet]:
        user = self.request.user
        queryset = super().get_queryset()
        queryset = queryset.filter_patient(user.id)
        return queryset


class DoctorUploadedFileUpdateAPIView(RetrieveUpdateAPIView):
    queryset = DoctorFile.objects.select_all()
    permission_classes = [IsDoctor]
    serializer_class = DoctorUploadedFileRetrieveSerializer
    parser_classes = (FileUploadParser,)
    lookup_field = 'id'

    def get_queryset(self) -> Type[QuerySet]:
        user = self.request.user
        queryset = super().get_queryset()
        queryset = queryset.filter_patient(user.id)
        return queryset

    @swagger_auto_schema(operation_description='Upload file...', )
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class PatientFileListAPIView(QuerySetMixin, ListAPIView):
    queryset = PatientFile.objects.select_all()
    permission_classes = [IsPatient]
    serializer_class = PatientFileListSerializer


class PatientFileRetrieveAPIView(RetrieveUpdateAPIView):
    queryset = PatientFile.objects.select_all()
    permission_classes = [IsOwner | IsDoctor]
    serializer_class = PatientFlieRetrieveSerializer
    parser_classes = (FileUploadParser,)
    lookup_field = 'id'


class PatientFileUploadAPIView(InputValueSupporter, CreateAPIView):
    queryset = PatientFile.objects.select_all()
    permission_classes = [IsPatient]
    serializer_class = PatientFileUploadSerializer
    parser_classes = (FileUploadParser,)

    fields_to_display = 'file_prescription',


class PatientUploadedFileListAPIView(ListAPIView):
    queryset = PatientFile.objects.select_all()
    permission_classes = [IsPatient]
    serializer_class = PatientUploadedFileListSerializer
    lookup_field = 'id'

    def get_queryset(self) -> Type[QuerySet]:
        user = self.request.user
        return super().get_queryset().filter_uploader(uploader_id=user.id).filter_unchecked_list()


class DoctorFileDownloadAPIView(RetrieveAPIView):
    queryset = DoctorFile.objects.all()
    permission_classes = [IsDoctor]
    serializer_class = DoctorFileDownloadSerializer
    lookup_field = 'id'

    def get(self, request, *args, **kwargs) -> 'FileResponse':
        file_object = self.get_object()
        downloader = Downloader(instance=file_object)
        return downloader.response()


class PatientFileDownloadAPIView(RetrieveAPIView):
    queryset = PatientFile.objects.all()
    permission_classes = [IsOwner | IsDoctor]
    serializer_class = PatientFileDownloadSerializer
    lookup_field = 'id'

    def get(self, request, *args, **kwargs) -> 'FileResponse':
        file_object = self.get_object()
        downloader = Downloader(instance=file_object)
        return downloader.response()
