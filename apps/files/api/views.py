from django.http import FileResponse
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, RetrieveUpdateAPIView
from rest_framework.parsers import FormParser, MultiPartParser

from accounts.api.permissions import IsDoctor, IsPatient, IsOwner
from files.api.mixins import QuerySetMixin
from files.api.serializers import FlieRetrieveSerializer, \
    FileDownloadSerializer, PatientFileUploadSerializer, DoctorFileUploadSerializer, \
    DoctorFileListSerializer, PatientFileListSerializer, PatientUploadedFileListSerializer, \
    DoctorUploadedFileListSerializer
from files.api.utils import Downloader
from files.models import DataFile


class DoctorDataFileListAPIView(QuerySetMixin, ListAPIView):
    permission_classes = [IsDoctor]
    serializer_class = DoctorFileListSerializer


class PatientDataFileListAPIView(QuerySetMixin, ListAPIView):
    # queryset = DataFile.objects.all()
    permission_classes = [IsPatient]
    serializer_class = PatientFileListSerializer


class DoctorDataFileUploadAPIView(QuerySetMixin, CreateAPIView):
    permission_classes = [IsDoctor]
    serializer_class = DoctorFileUploadSerializer
    parser_classes = (MultiPartParser, FormParser)


class PatientDataFileUploadAPIView(CreateAPIView):
    permission_classes = [IsPatient]
    serializer_class = PatientFileUploadSerializer
    parser_classes = (MultiPartParser, FormParser)


class DataFileRetrieveAPIView(RetrieveAPIView):
    queryset = DataFile.objects.all()
    permission_classes = [IsOwner | IsDoctor]
    serializer_class = FlieRetrieveSerializer
    lookup_field = 'id'


class DataFileDownloadAPIView(RetrieveAPIView):
    queryset = DataFile.objects.all()
    permission_classes = [IsOwner | IsDoctor]
    serializer_class = FileDownloadSerializer
    lookup_field = 'id'

    def get(self, request, *args, **kwargs) -> 'FileResponse':
        file_object = self.get_object()
        downloader = Downloader(instance=file_object)
        return downloader.response()


class DoctorUploadedFileListAPIView(ListAPIView):
    queryset = DataFile.objects.all()
    permission_classes = [IsDoctor]
    serializer_class = DoctorUploadedFileListSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset().join_uploader('uploader__doctor').unchecked_list()
        queryset = queryset.filter(uploader__patient__doctor_id=user.id)
        return queryset


class PatientUploadedFileListAPIView(ListAPIView):
    queryset = DataFile.objects.all()
    permission_classes = [IsPatient]
    serializer_class = PatientUploadedFileListSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        user = self.request.user
        return super().get_queryset().join_uploader('uploader__patient').filter(uploader_id=user.id).unchecked_list()


class DoctorUploadedFileUpdateAPIView(RetrieveUpdateAPIView):
    queryset = DataFile.objects.all()
    permission_classes = [IsDoctor]
    serializer_class = DoctorUploadedFileListSerializer
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset().unchecked_list()
        queryset = queryset.join_prescription_writer().filter(uploader__patient__doctor_id=user.id)
        return queryset

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
