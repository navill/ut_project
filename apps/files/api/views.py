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

    def get_queryset(self):
        return super(DataFileListAPIVIew, self).get_queryset().owner_queryset(self.request.user)


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

    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     headers = self.get_success_headers(serializer.data)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    #
    # def perform_create(self, serializer):
    #     serializer.save()
    #
    # def get_success_headers(self, data):
    #     try:
    #         return {'Location': str(data[api_settings.URL_FIELD_NAME])}
    #     except (TypeError, KeyError):
    #         return {}


class PatientDataFileUploadAPIView(CreateAPIView):
    queryset = DataFile.objects.all()
    permission_classes = []
    serializer_class = FileUploadSerializer
    parser_classes = (MultiPartParser, FormParser)


class DataFileDownloadAPIView(APIView):
    pass
