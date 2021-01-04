from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView

from files.api.serializers import FlieListSerializer, FileUploadSerializer, FlieRetrieveSerializer
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
    permission_classes = []
    serializer_class = FileUploadSerializer
    parser_classes = (MultiPartParser, FormParser)


class DataFileDownloadAPIView(APIView):
    pass
