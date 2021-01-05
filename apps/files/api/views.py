from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.views import APIView

from accounts.api.permissions import IsDoctor, IsPatient
from files.api.serializers import FlieListSerializer, FileUploadSerializer, FlieRetrieveSerializer, UploadedFileListSerializer
from files.models import DataFile


class DataFileListAPIVIew(ListAPIView):
    queryset = DataFile.objects.all()
    permission_classes = []
    # authentication_classes = []
    serializer_class = FlieListSerializer


class DataFileRetrieveAPIVIew(RetrieveAPIView):
    queryset = DataFile.objects.all()
    permission_classes = []
    # authentication_classes = []
    serializer_class = FlieRetrieveSerializer
    lookup_field = 'id'


class DoctorDataFileUploadAPIView(CreateAPIView):
    queryset = DataFile.objects.all()
    permission_classes = []
    # authentication_classes = []
    serializer_class = FileUploadSerializer
    parser_classes = (MultiPartParser, FormParser)


class PatientDataFileUploadAPIView(CreateAPIView):
    queryset = DataFile.objects.all()
    permission_classes = [IsPatient]
    serializer_class = FileUploadSerializer
    parser_classes = (MultiPartParser, FormParser)


class DataFileDownloadAPIView(APIView):
    pass


class UploadedFileListAPIView(ListAPIView):
    queryset = DataFile.objects.all()
    # permission_classes = []
    permission_classes = [IsDoctor]
    serializer_class = UploadedFileListSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.get_unchecked_list().filter_current_user(uploader=self.request.user)
        return queryset
