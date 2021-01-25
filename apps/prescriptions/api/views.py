import json
from typing import Optional, Type

from django.db.models import QuerySet
from rest_framework.generics import RetrieveUpdateAPIView, ListAPIView, RetrieveAPIView, \
    CreateAPIView
from rest_framework.response import Response

from accounts.api.permissions import IsDoctor, IsOwner, RelatedPatientReadOnly, IsPatient
from accounts.models import Patient
from prescriptions.api import serializers
from prescriptions.api.serializers import PrescriptionSerializer, PrescriptionCreateSerializer, \
    FilePrescriptionListSerializer, FilePrescriptionCreateSerializer, FilePrescriptionRetrieveUpdateSerializer, \
    NestedPrescriptionSerializer
from prescriptions.models import Prescription, FilePrescription, HealthStatus


class PrescriptionListAPIView(ListAPIView):
    queryset = Prescription.objects.select_all().prefetch_doctor_file()  # .defer_option_fields()
    serializer_class = PrescriptionSerializer
    permission_classes = [IsDoctor | IsPatient]
    lookup_field = 'pk'

    def get_queryset(self) -> Optional[Type[QuerySet]]:
        queryset = super().get_queryset()

        user = self.request.user

        if user.is_doctor:
            return queryset.filter_writer(writer_id=user.id)
        elif user.is_patient:
            return queryset.filter_patient(patient_id=user.id)
        else:
            return queryset if user.is_superuser else None


class PrescriptionCreateAPIView(CreateAPIView):
    """
    {
        "patient": "select 'user_id'",
        "status": "select 'status'",
        "upload_doctor_files": "List type File field"
    }
    """
    queryset = Prescription.objects.select_all().prefetch_doctor_file()  # .defer_option_fields()
    serializer_class = PrescriptionCreateSerializer
    # permission_classes = [IsDoctor | IsPatient]
    permission_classes = []

    def get(self, request, *args, **kwargs):
        user = request.user
        doc_values = self.__doc__
        default_values = json.loads(doc_values)
        patients = Patient.objects.filter(doctor_id=user.id).values()
        default_values['patient'] = patients
        default_values['status'] = HealthStatus.choices
        return Response(default_values)


class PrescriptionRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Prescription.objects.select_all()  # .defer_option_fields()
    serializer_class = PrescriptionSerializer
    permission_classes = [IsOwner | RelatedPatientReadOnly]
    lookup_field = 'pk'

    def perform_update(self,
                       serializer: serializers.PrescriptionSerializer):
        serializer.save()


class FilePrescriptionListAPIView(ListAPIView):
    queryset = FilePrescription.objects.all()
    serializer_class = FilePrescriptionListSerializer
    permission_classes = [IsDoctor | IsPatient]

    def get_queryset(self) -> Optional[QuerySet]:
        queryset = super().get_queryset()
        user = self.request.user

        if user.is_doctor:
            return queryset.filter(prescription__writer_id=user.id)
        elif user.is_patient:
            return queryset.filter(prescription__patient_id=user.id)
        else:
            return queryset if user.is_superuser else None


class FilePrescriptionCreateAPIView(CreateAPIView):
    """
    {
        "prescription": "select 'id'",
        "status": "select 'status'"
    }
    """
    queryset = FilePrescription.objects.all()
    serializer_class = FilePrescriptionCreateSerializer
    permission_classes = [IsDoctor]

    def get(self, request, *args, **kwargs):
        user = self.request.user
        doc_values = self.__doc__
        default_values = json.loads(doc_values)

        prescriptions = Prescription.objects.filter(writer_id=user.id).values('id', 'writer_name', 'patient_name',
                                                                              'created_at')
        default_values['prescription'] = prescriptions
        default_values['status'] = HealthStatus.choices
        return Response(default_values)


class FilePrescriptionRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    queryset = FilePrescription.objects.all()
    serializer_class = FilePrescriptionRetrieveUpdateSerializer
    permission_classes = [IsOwner | RelatedPatientReadOnly]
    lookup_field = 'pk'


class TestPrescriptionAPIView(RetrieveAPIView):
    queryset = Prescription.objects.nested_all()  # + defer_option_fields()
    serializer_class = NestedPrescriptionSerializer
    permission_classes = [IsOwner | RelatedPatientReadOnly]
    lookup_field = 'pk'
