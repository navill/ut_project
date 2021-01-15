from django.http import FileResponse
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, RetrieveUpdateAPIView
from rest_framework.parsers import FormParser, MultiPartParser

from accounts.api.permissions import IsDoctor, IsPatient, IsOwner
from files.api.mixins import QuerySetMixin
from files.api.serializers import FlieRetrieveSerializer, \
    FileDownloadSerializer, PatientFileUploadSerializer, DoctorFileUploadSerializer, \
    DoctorFileListSerializer, PatientFileListSerializer, PatientUploadedFileListSerializer, \
    DoctorUploadedFileListSerializer, DoctorUploadedFileRetrieveSerializer
from files.api.utils import Downloader
from files.models import DataFile


class DoctorDataFileListAPIView(QuerySetMixin, ListAPIView):
    permission_classes = [IsDoctor]
    serializer_class = DoctorFileListSerializer


class DoctorDataFileUploadAPIView(QuerySetMixin, CreateAPIView):
    permission_classes = [IsDoctor]
    serializer_class = DoctorFileUploadSerializer
    parser_classes = (MultiPartParser, FormParser)


class DoctorUploadedFileListAPIView(ListAPIView):
    queryset = DataFile.objects.select_all()
    permission_classes = [IsDoctor]
    serializer_class = DoctorUploadedFileListSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset().filter_unchecked_list()
        queryset = queryset.filter(uploader__patient__doctor_id=user.id)
        return queryset


class DoctorUploadedFileUpdateAPIView(RetrieveUpdateAPIView):
    queryset = DataFile.objects.select_all()
    permission_classes = [IsDoctor]
    serializer_class = DoctorUploadedFileRetrieveSerializer
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset().filter_unchecked_list()
        queryset = queryset.filter(uploader__patient__doctor_id=user.id)
        return queryset

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class PatientDataFileListAPIView(QuerySetMixin, ListAPIView):
    permission_classes = [IsPatient]
    serializer_class = PatientFileListSerializer


class PatientDataFileUploadAPIView(CreateAPIView):
    permission_classes = [IsPatient]
    serializer_class = PatientFileUploadSerializer
    parser_classes = (MultiPartParser, FormParser)


class PatientUploadedFileListAPIView(ListAPIView):
    queryset = DataFile.objects.select_patient()
    permission_classes = [IsPatient]
    serializer_class = PatientUploadedFileListSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        user = self.request.user
        return super().get_queryset().filter(uploader_id=user.id).filter_unchecked_list()


class DataFileRetrieveAPIView(RetrieveAPIView):
    queryset = DataFile.objects.select_all()
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
