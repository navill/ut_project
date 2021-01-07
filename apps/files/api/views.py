from django.http import FileResponse
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView
from rest_framework.parsers import FormParser, MultiPartParser

from accounts.api.permissions import IsDoctor, IsPatient, IsOwner
from files.api.serializers import FlieListSerializer, FileUploadSerializer, FlieRetrieveSerializer, \
    UploadedFileListSerializer, FileDownloadSerializer
from files.api.utils import Downloader
from files.models import DataFile


class DataFileListAPIView(ListAPIView):
    queryset = DataFile.objects.all()
    permission_classes = [IsDoctor | IsPatient]
    serializer_class = FlieListSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = super(DataFileListAPIView, self).get_queryset().necessary_fields()
        if user.is_superuser:
            return queryset
        return queryset.filter_current_user(uploader=user)


class DoctorDataFileUploadAPIView(CreateAPIView):
    permission_classes = [IsDoctor]
    serializer_class = FileUploadSerializer
    parser_classes = (MultiPartParser, FormParser)


class PatientDataFileUploadAPIView(CreateAPIView):
    permission_classes = [IsPatient]
    serializer_class = FileUploadSerializer
    parser_classes = (MultiPartParser, FormParser)


class DataFileRetrieveAPIView(RetrieveAPIView):
    queryset = DataFile.objects.all()
    permission_classes = [IsOwner]
    serializer_class = FlieRetrieveSerializer
    lookup_field = 'id'


class DataFileDownloadAPIView(RetrieveAPIView):
    queryset = DataFile.objects.all()
    permission_classes = [IsOwner]
    serializer_class = FileDownloadSerializer
    lookup_field = 'id'

    def get(self, request, *args, **kwargs) -> 'FileResponse':
        file_object = self.get_object()
        downloader = Downloader(instance=file_object)
        return downloader.response()


class UploadedFileListAPIView(ListAPIView):
    queryset = DataFile.objects.all()
    permission_classes = [IsDoctor | IsPatient]
    serializer_class = UploadedFileListSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset().necessary_fields('checked')
        return queryset.unchecked_list().filter_current_user(uploader=user)
