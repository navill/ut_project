from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView, RetrieveAPIView

from accounts.models import Doctor, Patient
from core.api.serializers import (DoctorNestedPatientSerializer,
                                  PatientNestedPrescriptionSerializer,
                                  DoctorUpdateSerializer,
                                  PrescriptionNestedFilePrescriptionSerializer,
                                  FilePrescriptionNestedPatientFileSerializer)
from prescriptions.models import Prescription, FilePrescription


# doctor - main

class DoctorNestedPatients(RetrieveAPIView):
    queryset = Doctor.objects.select_all()
    permission_classes = []
    authentication_classes = []
    serializer_class = DoctorNestedPatientSerializer
    lookup_field = 'pk'


class PatientNestedPrescriptions(RetrieveAPIView):
    queryset = Patient.objects.select_all().prefetch_all()
    permission_classes = []
    authentication_classes = []
    serializer_class = PatientNestedPrescriptionSerializer
    lookup_field = 'pk'


class DoctorUpdate(RetrieveUpdateAPIView):
    queryset = Doctor.objects.select_all()
    permission_classes = []
    authentication_classes = []
    serializer_class = DoctorUpdateSerializer
    lookup_field = 'pk'


class PrescriptionNestedFilePrescriptions(RetrieveAPIView):
    queryset = Prescription.objects.select_all()
    permission_classes = []
    authentication_classes = []
    serializer_class = PrescriptionNestedFilePrescriptionSerializer
    lookup_field = 'pk'


class FilePrescriptionNestedPatientFiles(RetrieveAPIView):
    queryset = FilePrescription.objects.select_all()
    permission_classes = []
    authentication_classes = []
    serializer_class = FilePrescriptionNestedPatientFileSerializer
    lookup_field = 'pk'

# patient - main
