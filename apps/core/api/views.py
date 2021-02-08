from django.db.models import Prefetch
from rest_framework.generics import RetrieveAPIView, ListAPIView, RetrieveUpdateAPIView, CreateAPIView

from accounts.api.permissions import IsDoctor, IsOwner, IsPatient
from accounts.models import Doctor, Patient
from config.utils.api_utils import InputValueSupporter
from core.api.serializers import (DoctorNestedPatientSerializer,
                                  PatientNestedPrescriptionSerializer,
                                  PrescriptionNestedFilePrescriptionSerializer,
                                  FilePrescriptionNestedPatientFileSerializer,
                                  ExpiredFilePrescriptionHistorySerializer,
                                  UploadedPatientFileHistorySerializer, PatientWithDoctorSerializer,
                                  FilePrescriptionsForPatientSerializer,
                                  PatientMainSerializer, PrescriptionNestedDoctorFileSerializer,
                                  PrescriptionListForPatientSerializer,
                                  )
from files.models import PatientFile, DoctorFile
from prescriptions.api.mixins import HistoryMixin
from prescriptions.api.serializers import PrescriptionCreateSerializer
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


class PrescriptionListForPatient(ListAPIView):  # 환자와 관련된 소견서 + 의사 파일 + FilePrescriptionList
    queryset = Prescription.objects.select_all()
    permission_classes = []
    serializer_class = PrescriptionListForPatientSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user_id = self.request.user.id
        prescriptions = queryset.filter(patient_id=user_id)
        return prescriptions


class PrescriptionDetailForPatient(RetrieveAPIView):
    queryset = Prescription.objects.select_all()
    permission_classes = []
    # permission_classes = ['PatientReadOnly']
    serializer_class = PrescriptionNestedDoctorFileSerializer
    lookup_field = 'pk'


class FilePrescriptionListForPatient(ListAPIView):  # Detail FilePrescription + PatietFile
    queryset = FilePrescription.objects.select_all()
    # permission_classes = [IsPatient]
    permission_classes = []
    serializer_class = FilePrescriptionsForPatientSerializer


class FilePrescriptionDetailForPatient(RetrieveAPIView):
    queryset = FilePrescription.objects.select_all()
    permission_classes = []
    serializer_class = FilePrescriptionNestedPatientFileSerializer
    lookup_field = 'pk'


class PatientMain(RetrieveAPIView):
    queryset = Patient.objects.select_all(). \
        prefetch_prescription(Prefetch('prescriptions', queryset=Prescription.objects.select_all().only_list())). \
        with_latest_prescription(). \
        only_detail('updated_at')
    permission_classes = []
    serializer_class = PatientMainSerializer
    lookup_field = 'pk'


# patient - history
class ChecekdFilePrescription(ListAPIView):  # 환자가 올린 파일을 의사가 확인(checked=True)한 리스트
    pass


# 210208 추가
# doctor
# todo: add doctor detail, patient detail, prescription detail, file prescription detail

# 기존의 기능을 끌어쓰는 것 보다 core-api용 view를 생성
# => 접근(permission) 처리 용이 및 구조적으로 core-api에서 .../patients/5/detail 이렇게 접근하는 것이 어색해보임
# 단순히 의사 및 환자에 따라 read & write 구분이 필요할 경우 공통으로 core view를 사용하고 permission으로 접근을 제어할 예정
class DoctorProfile(RetrieveUpdateAPIView):
    queryset = Doctor.objects.select_all()
    permission_classes = []  # owner readonly
    serializer_class = []
    lookup_field = 'pk'


class PatientProfile(RetrieveAPIView):
    queryset = Patient.objects.select_all()
    permission_classes = []  # owner readonly
    serializer_class = []
    lookup_field = 'pk'


# class PrescriptionCreate(InputValueSupporter, CreateAPIView):
#     queryset = Prescription.objects.select_all().prefetch_doctor_file()  # .defer_option_fields()
#     serializer_class = PrescriptionCreateSerializer
#     # permission_classes = [IsDoctor]
#     permission_classes = []
#     fields_to_display = 'patient', 'status'


class PrescriptionDetail(RetrieveUpdateAPIView):
    queryset = Prescription.objects.select_all()
    permission_classes = []  # only owner
    serializer_class = []
    lookup_field = 'pk'


class DoctorFileUpload(CreateAPIView):
    queryset = DoctorFile.objects.select_all()
    permission_classes = []  # only doctor
    serializer_class = []
    lookup_field = 'pk'


class DoctorFileDetail(RetrieveUpdateAPIView):
    queryset = DoctorFile.objects.select_all()
    permission_classes = []  # only owner
    serializer_class = []
    lookup_field = 'pk'


class FilePrescriptionDetail(RetrieveUpdateAPIView):
    queryset = FilePrescription.objects.select_all()
    permission_classes = []  # only owner
    serializer_class = []
    lookup_field = 'pk'


# patient
# todo: add patient detail, doctor detail, prescription detail, file prescription detail/upload
class DoctorProfileForPatient(RetrieveAPIView):
    queryset = Doctor.objects.select_all()
    permission_classes = []  # owner readonly
    serializer_class = []
    lookup_field = 'pk'


class PatientProfileForPatient(RetrieveUpdateAPIView):
    queryset = Patient.objects.select_all()
    permission_classes = []  # onwer readonly
    serializer_class = []
    lookup_field = 'pk'


class PatientFileUpload(CreateAPIView):
    queryset = PatientFile.objects.select_all()
    permission_classes = [IsPatient]
    serializer_class = []


class PatientFileDetail(RetrieveUpdateAPIView):
    queryset = PatientFile.objects.select_all()
    permission_classes = [IsPatient]
    serializer_class = []
