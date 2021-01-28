from typing import Optional, Type

from django.db.models import QuerySet
from rest_framework.generics import RetrieveUpdateAPIView, ListAPIView, RetrieveAPIView, \
    CreateAPIView

from accounts.api.permissions import IsDoctor, IsOwner, RelatedPatientReadOnly, IsPatient
from config.utils import InputValueSupporter
from prescriptions.api import serializers
from prescriptions.api.serializers import PrescriptionSerializer, PrescriptionCreateSerializer, \
    FilePrescriptionListSerializer, FilePrescriptionCreateSerializer, FilePrescriptionRetrieveUpdateSerializer, \
    NestedPrescriptionSerializer
from prescriptions.models import Prescription, FilePrescription


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


class PrescriptionCreateAPIView(InputValueSupporter, CreateAPIView):
    queryset = Prescription.objects.select_all().prefetch_doctor_file()  # .defer_option_fields()
    serializer_class = PrescriptionCreateSerializer
    # permission_classes = [IsDoctor]
    permission_classes = []
    fields_to_display = 'patient', 'status'


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


class FilePrescriptionCreateAPIView(InputValueSupporter, CreateAPIView):
    queryset = FilePrescription.objects.all()
    serializer_class = FilePrescriptionCreateSerializer
    permission_classes = [IsDoctor]
    fields_to_display = 'prescription', 'status'


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
