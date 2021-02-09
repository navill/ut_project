from rest_framework.generics import RetrieveUpdateAPIView, RetrieveAPIView, CreateAPIView

from accounts.api.permissions import IsDoctor, IsOwner, RelatedPatientReadOnly, IsPatient
from config.utils.api_utils import InputValueSupporter
from prescriptions.api import serializers
from prescriptions.api.serializers import (PrescriptionSerializer,
                                           PrescriptionCreateSerializer,
                                           FilePrescriptionListSerializer,
                                           FilePrescriptionCreateSerializer,
                                           FilePrescriptionRetrieveUpdateSerializer,
                                           NestedPrescriptionSerializer)
from prescriptions.api.utils import CommonListAPIView
from prescriptions.models import Prescription, FilePrescription


class PrescriptionListAPIView(CommonListAPIView):
    queryset = Prescription.objects.select_all().prefetch_doctor_file()  # .defer_option_fields()
    serializer_class = PrescriptionSerializer
    permission_classes = [IsDoctor | IsPatient]
    lookup_field = 'pk'


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

    def perform_update(self, serializer: serializers.PrescriptionSerializer):
        serializer.save()


class FilePrescriptionListAPIView(CommonListAPIView):
    queryset = FilePrescription.objects.all()
    serializer_class = FilePrescriptionListSerializer
    permission_classes = [IsDoctor | IsPatient]


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
