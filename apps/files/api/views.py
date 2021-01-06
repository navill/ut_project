from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.views import APIView

from accounts.api.permissions import IsDoctor, IsPatient, IsOwner
from files.api.serializers import FlieListSerializer, FileUploadSerializer, FlieRetrieveSerializer, \
    UploadedFileListSerializer
from files.models import DataFile


class DataFileListAPIView(ListAPIView):
    queryset = DataFile.objects.all()
    permission_classes = [IsDoctor | IsPatient]
    # authentication_classes = []
    serializer_class = FlieListSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        return queryset.related_uploader(uploader=user).filter_current_user(uploader=user)


class DoctorDataFileUploadAPIView(CreateAPIView):
    permission_classes = [IsDoctor]
    # authentication_classes = []
    serializer_class = FileUploadSerializer
    parser_classes = (MultiPartParser, FormParser)


class PatientDataFileUploadAPIView(CreateAPIView):
    permission_classes = [IsPatient]
    # authentication_classes = []
    serializer_class = FileUploadSerializer
    parser_classes = (MultiPartParser, FormParser)


class DataFileRetrieveAPIView(RetrieveAPIView):
    queryset = DataFile.objects.all()
    permission_classes = [IsOwner]
    # authentication_classes = []
    serializer_class = FlieRetrieveSerializer
    lookup_field = 'id'


class DataFileDownloadAPIView(APIView):
    pass


class UploadedFileListAPIView(ListAPIView):
    queryset = DataFile.objects.all()
    # permission_classes = []
    permission_classes = [IsDoctor | IsPatient]
    serializer_class = UploadedFileListSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset().necessary_fields('checked', 'file')
        return queryset.unchecked_list().filter_current_user(uploader=user)
