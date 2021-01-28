from rest_framework.generics import RetrieveAPIView, ListAPIView

from accounts.api.permissions import IsDoctor, IsOwner
from accounts.models import Doctor, Patient
from core.api.serializers import (DoctorNestedPatientSerializer,
                                  PatientNestedPrescriptionSerializer,
                                  PrescriptionNestedFilePrescriptionSerializer,
                                  FilePrescriptionNestedPatientFileSerializer,
                                  ExpiredFilePrescriptionHistorySerializer,
                                  UploadedPatientFileHistorySerializer,
                                  )
from prescriptions.api.mixins import HistoryMixin
from prescriptions.models import Prescription, FilePrescription


# doctor - main
class DoctorNestedPatients(RetrieveAPIView):
    queryset = Doctor.objects.select_all()
    permission_classes = [IsOwner]
    serializer_class = DoctorNestedPatientSerializer
    lookup_field = 'pk'


class PatientNestedPrescriptions(RetrieveAPIView):
    queryset = Patient.objects.select_all().prefetch_prescription_with_writer()
    permission_classes = [IsDoctor]
    serializer_class = PatientNestedPrescriptionSerializer
    lookup_field = 'pk'


class PrescriptionNestedFilePrescriptions(RetrieveAPIView):
    queryset = Prescription.objects.select_all()
    permission_classes = [IsDoctor]
    serializer_class = PrescriptionNestedFilePrescriptionSerializer
    lookup_field = 'pk'


class FilePrescriptionNestedPatientFiles(RetrieveAPIView):
    queryset = FilePrescription.objects.nested_all()
    permission_classes = [IsDoctor]
    serializer_class = FilePrescriptionNestedPatientFileSerializer
    lookup_field = 'pk'


# doctor - history
class UploadedPatientFileHistory(HistoryMixin, ListAPIView):
    queryset = FilePrescription.objects.nested_all()
    permission_classes = [IsDoctor]
    serializer_class = UploadedPatientFileHistorySerializer

    def get_queryset(self):
        queryset = self.get_mixin_queryset()
        return queryset.filter_new_uploaded_file()


class ExpiredFilePrescriptionHistory(HistoryMixin, ListAPIView):
    queryset = FilePrescription.objects.nested_all()
    permission_classes = [IsDoctor]
    serializer_class = ExpiredFilePrescriptionHistorySerializer

    def get_queryset(self):
        queryset = self.get_mixin_queryset()
        return queryset.filter_upload_date_expired()
