from rest_framework.generics import RetrieveAPIView, ListAPIView

from accounts.api.permissions import IsDoctor, IsOwner
from accounts.models import Doctor, Patient
from core.api.serializers import (DoctorNestedPatientSerializer,
                                  PatientNestedPrescriptionSerializer,
                                  PrescriptionNestedFilePrescriptionSerializer,
                                  FilePrescriptionNestedPatientFileSerializer,
                                  ExpiredFilePrescriptionHistorySerializer,
                                  UploadedPatientFileHistorySerializer, PatientWithDoctorSerializer,
                                  PrescriptionsRelatedPatientSerializer, FilePrescriptionsSerializer,
                                  PatientMainSerializer,
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
    queryset = FilePrescription.objects.nested_all().filter_new_uploaded_file()
    permission_classes = [IsDoctor]
    serializer_class = UploadedPatientFileHistorySerializer


class ExpiredFilePrescriptionHistory(HistoryMixin, ListAPIView):
    queryset = FilePrescription.objects.nested_all().filter_upload_date_expired()
    permission_classes = [IsDoctor]
    serializer_class = ExpiredFilePrescriptionHistorySerializer


# Patient - main
class PatientWithDoctor(RetrieveAPIView):  # 환자 첫 페이지 - 담당 의사 정보 포함
    queryset = Patient.objects.select_all()
    # permission_classes = [IsPatient]
    permission_classes = []
    serializer_class = PatientWithDoctorSerializer
    lookup_field = 'pk'


class PrescriptionsRelatedPatient(RetrieveAPIView):  # 환자와 관련된 소견서 + 의사 파일 + FilePrescriptionList
    queryset = Prescription.objects.select_all()
    # permission_classes = [IsPatient]
    permission_classes = []
    serializer_class = PrescriptionsRelatedPatientSerializer
    lookup_field = 'pk'


class FilePrescriptionList(ListAPIView):  # Detail FilePrescription + PatietFile
    queryset = FilePrescription.objects.select_all()
    # permission_classes = [IsPatient]
    permission_classes = []
    serializer_class = FilePrescriptionsSerializer
    # lookup_field = 'pk'


class PatientMain(RetrieveAPIView):
    queryset = Patient.objects.select_all().prefetch_prescription().with_latest_prescription()
    # queryset = Patient.objects.all()
    permission_classes = []
    serializer_class = PatientMainSerializer
    lookup_field = 'pk'


# patient - history
class ChecekdFilePrescription(ListAPIView):  # 환자가 올린 파일을 의사가 확인(checked=True)한 리스트
    pass

#
# class PatientMainSchedule(ListAPIView):  # 환자가 파일을 업로드해야하는 날짜(FilePrescriptionList)
#     queryset = FilePrescription.objects.all()
#     permission_classes = []
#     serializer_class = PatientMainScheduleSerializer
