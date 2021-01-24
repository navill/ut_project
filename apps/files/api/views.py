import json
from typing import Type

from django.db.models import QuerySet
from django.http import FileResponse
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, RetrieveUpdateAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from accounts.api.permissions import IsDoctor, IsPatient, IsOwner
from files.api.mixins import QuerySetMixin
from files.api.serializers import PatientFileUploadSerializer, DoctorFileUploadSerializer, \
    DoctorFileListSerializer, PatientFileListSerializer, PatientUploadedFileListSerializer, \
    DoctorUploadedFileListSerializer, DoctorFlieRetrieveSerializer, DoctorUploadedFileRetrieveSerializer, \
    PatientFlieRetrieveSerializer, DoctorFileDownloadSerializer, PatientFileDownloadSerializer
from files.api.utils import Downloader
from files.models import DoctorFile, PatientFile
from prescriptions.models import Prescription, FilePrescription


class DoctorFileListAPIView(QuerySetMixin, ListAPIView):
    queryset = DoctorFile.objects.select_all()
    permission_classes = [IsDoctor]
    serializer_class = DoctorFileListSerializer


class DoctorFileRetrieveAPIView(RetrieveAPIView):
    queryset = DoctorFile.objects.select_all()
    permission_classes = [IsOwner | IsDoctor]
    serializer_class = DoctorFlieRetrieveSerializer
    lookup_field = 'id'


class DoctorFileUploadAPIView(QuerySetMixin, CreateAPIView):
    """
    {
        "prescription": "prescription id"
    }
    """
    queryset = DoctorFile.objects.select_all()
    permission_classes = [IsDoctor]
    serializer_class = DoctorFileUploadSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, *args, **kwargs):
        user = request.user
        doc_values = self.__doc__
        default_values = json.loads(doc_values)
        prescriptions = Prescription.objects.select_all().filter_writer(writer_id=user.id).values('id',
                                                                                                  'status',
                                                                                                  'writer_name',
                                                                                                  'patient_name',
                                                                                                  'created_at')
        default_values['prescription'] = prescriptions

        return Response(default_values)


class DoctorUploadedFileListAPIView(ListAPIView):
    queryset = DoctorFile.objects.select_all()
    permission_classes = [IsDoctor]
    serializer_class = DoctorUploadedFileListSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self) -> Type[QuerySet]:
        user = self.request.user
        queryset = super().get_queryset()
        queryset = queryset.filter_patient(user.id)
        return queryset


class DoctorUploadedFileUpdateAPIView(RetrieveUpdateAPIView):
    queryset = DoctorFile.objects.select_all()
    permission_classes = [IsDoctor]
    serializer_class = DoctorUploadedFileRetrieveSerializer
    lookup_field = 'id'

    def get_queryset(self) -> Type[QuerySet]:
        user = self.request.user
        queryset = super().get_queryset()
        queryset = queryset.filter_patient(user.id)
        return queryset

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class PatientFileListAPIView(QuerySetMixin, ListAPIView):
    queryset = PatientFile.objects.select_all()
    permission_classes = [IsPatient]
    serializer_class = PatientFileListSerializer


class PatientFileRetrieveAPIView(RetrieveAPIView):
    queryset = PatientFile.objects.select_all()
    permission_classes = [IsOwner | IsDoctor]
    serializer_class = PatientFlieRetrieveSerializer
    lookup_field = 'id'


class PatientFileUploadAPIView(CreateAPIView):
    """
    {
        "file_prescription": "select 'id'"
    }
    """
    permission_classes = [IsPatient]
    serializer_class = PatientFileUploadSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, *args, **kwargs):
        user = request.user
        doc_values = self.__doc__
        default_values = json.loads(doc_values)
        prescription = Prescription.objects.filter(patient_id=user.id).last()
        file_prescriptions = FilePrescription.objects. \
            filter(prescription_id=prescription.id). \
            filter(active=True, uploaded=False). \
            values('id', 'created_at', 'day_number')
        default_values['file_prescription'] = file_prescriptions
        return Response(file_prescriptions)


class PatientUploadedFileListAPIView(ListAPIView):
    queryset = PatientFile.objects.select_all()
    permission_classes = [IsPatient]
    serializer_class = PatientUploadedFileListSerializer
    parser_classes = (MultiPartParser, FormParser)
    lookup_field = 'id'

    def get_queryset(self) -> Type[QuerySet]:
        user = self.request.user
        return super().get_queryset().filter_uploader(uploader_id=user.id).filter_unchecked_list()


class DoctorFileDownloadAPIView(RetrieveAPIView):
    queryset = DoctorFile.objects.all()
    permission_classes = [IsOwner | IsDoctor]
    serializer_class = DoctorFileDownloadSerializer
    lookup_field = 'id'

    def get(self, request, *args, **kwargs) -> 'FileResponse':
        file_object = self.get_object()
        downloader = Downloader(instance=file_object)
        return downloader.response()


class PatientFileDownloadAPIView(RetrieveAPIView):
    queryset = PatientFile.objects.all()
    permission_classes = [IsOwner]
    serializer_class = PatientFileDownloadSerializer
    lookup_field = 'id'

    def get(self, request, *args, **kwargs) -> 'FileResponse':
        file_object = self.get_object()
        downloader = Downloader(instance=file_object)
        return downloader.response()
