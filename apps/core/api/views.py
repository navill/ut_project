from django.db.models import Prefetch
from rest_framework.generics import RetrieveAPIView, ListAPIView, RetrieveUpdateAPIView, CreateAPIView, DestroyAPIView
from rest_framework.parsers import MultiPartParser, FileUploadParser

from accounts.api.permissions import IsDoctor, IsOwner, IsPatient, CareDoctorReadOnly
from accounts.api.serializers import DoctorDetailSerializer, PatientDetailSerializer
from accounts.models import Doctor, Patient
from config.utils.api_utils import InputValueSupporter
from core.api.serializers import (DoctorWithPatientSerializer,
                                  PatientWithPrescriptionSerializer,
                                  PrescriptionNestedFilePrescriptionSerializer,
                                  FilePrescriptionNestedPatientFileSerializer,
                                  ExpiredFilePrescriptionHistorySerializer,
                                  UploadedPatientFileHistorySerializer,
                                  PatientWithDoctorSerializer,
                                  FilePrescriptionsForPatientSerializer,
                                  PatientMainSerializer,
                                  PrescriptionWithDoctorFileSerializer,
                                  PrescriptionListForPatientSerializer,
                                  )
from files.api.serializers import DoctorFileUploadSerializer, DoctorFlieRetrieveSerializer, \
    PatientFlieRetrieveSerializer, PatientFileUploadSerializer
from files.models import PatientFile, DoctorFile
from prescriptions.api.mixins import HistoryMixin
from prescriptions.api.serializers import PrescriptionCreateSerializer, \
    PrescriptionDetailSerializer, FilePrescriptionDetailSerializer

from prescriptions.models import Prescription, FilePrescription


# todo(improve): serializer 정리
# core.serializer: core-url을 포함하는 serializer
# <app_name>.serializer: 각 앱에 위치한 default serializer

# doctor - main
class DoctorWithPatients(RetrieveAPIView):
    """
    로그인 시 의사 정보와 의사가 담당하는 환자의 리스트를 출력
    ---

    """
    queryset = Doctor.objects.select_all()
    permission_classes = [IsOwner]
    serializer_class = DoctorWithPatientSerializer
    lookup_field = 'pk'


class PatientWithPrescriptions(RetrieveAPIView):
    """
    의사가 작성한 해당 환자의 소견서 리스트
    ---

    """
    queryset = Patient.objects.select_all().prefetch_prescription_with_writer()
    permission_classes = [IsDoctor]
    serializer_class = PatientWithPrescriptionSerializer
    lookup_field = 'pk'


class PrescriptionWithFilePrescriptions(RetrieveAPIView):
    """
    소견서에 등록된 파일 업로드 일정(FilePrescription)
    ---

    """
    queryset = Prescription.objects.select_all()
    permission_classes = [IsDoctor]
    serializer_class = PrescriptionNestedFilePrescriptionSerializer
    lookup_field = 'pk'


class FilePrescriptionWithPatientFiles(RetrieveUpdateAPIView):
    """
    파일 업로드 일정에 등록된 환자가 올린 파일 정보
    ---

    """
    queryset = FilePrescription.objects.nested_all()
    permission_classes = [IsDoctor]
    serializer_class = FilePrescriptionNestedPatientFileSerializer
    lookup_field = 'pk'


# doctor - history
class UploadedPatientFileHistory(HistoryMixin, ListAPIView):
    """
    환자가 새로운 파일을 업로드 했을 때 보여지는 리스트(FilePrescription)
    ---

    """
    queryset = FilePrescription.objects.nested_all().filter_new_uploaded_file()
    permission_classes = [IsDoctor]
    serializer_class = UploadedPatientFileHistorySerializer


class ExpiredFilePrescriptionHistory(HistoryMixin, ListAPIView):
    """
    환자가 일정 내에 파일을 업로드 하지 않았을 경우 보여지는 리스트(FilePrescription)
    ---

    """
    queryset = FilePrescription.objects.nested_all().filter_upload_date_expired()
    permission_classes = [IsDoctor]
    serializer_class = ExpiredFilePrescriptionHistorySerializer


# Patient - main
class PatientWithDoctor(RetrieveAPIView):  # 환자 첫 페이지 - 담당 의사 정보 포함
    """
    담당 의사 정보를 포함하는 환자의 첫 페이지
    ---

    """
    queryset = Patient.objects.select_all()
    # permission_classes = [IsPatient]
    permission_classes = []
    serializer_class = PatientWithDoctorSerializer
    lookup_field = 'pk'


class PrescriptionListForPatient(ListAPIView):  # 환자와 관련된 소견서 + 의사 파일 + FilePrescriptionList
    """
    해당 환자에 대해 작성된 소견서 리스트
    ---

    """

    queryset = Prescription.objects.select_all()
    permission_classes = []
    serializer_class = PrescriptionListForPatientSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user_id = self.request.user.id
        prescriptions = queryset.filter(patient_id=user_id)
        return prescriptions


class PrescriptionDetailForPatient(RetrieveAPIView):
    """
    환자가 접근할 수 있는 소견서의 세부 정보
    ---

    """
    queryset = Prescription.objects.select_all()
    permission_classes = []
    # permission_classes = ['PatientReadOnly']
    serializer_class = PrescriptionWithDoctorFileSerializer
    lookup_field = 'pk'


class FilePrescriptionListForPatient(ListAPIView):  # Detail FilePrescription + PatietFile
    """
    환자가 접근할 수 있는 파일 업로드 일정 리스트
    ---

    """
    queryset = FilePrescription.objects.select_all()
    # permission_classes = [IsPatient]
    permission_classes = []
    serializer_class = FilePrescriptionsForPatientSerializer


class FilePrescriptionDetailForPatient(RetrieveAPIView):
    """
    환자가 접근할 수 있는 파일 업로드 일정의 세부 정보
    ---

    """
    queryset = FilePrescription.objects.select_all()
    permission_classes = []
    serializer_class = FilePrescriptionNestedPatientFileSerializer
    lookup_field = 'pk'


class PatientMain(RetrieveAPIView):
    """
    환자용 메인 페이지
    ---

    """
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
# 기존의 기능을 끌어쓰는 것 보다 core-api용 view를 생성
# => 접근(permission) 처리 용이 및 구조적으로 core-api에서 .../patients/5/detail 이렇게 접근하는 것이 어색해보임
# 단순히 의사 및 환자에 따라 read & write 구분이 필요할 경우 공통으로 core view를 사용하고 permission으로 접근을 제어할 예정
class DoctorProfile(RetrieveUpdateAPIView):
    """
    의사의 프로필 접근 및 수정
    ---

    """
    queryset = Doctor.objects.select_all()
    permission_classes = [IsOwner]  # owner readonly
    serializer_class = DoctorDetailSerializer
    lookup_field = 'pk'


class PatientProfile(RetrieveAPIView):
    """
    환자의 프로필 접근(의사용)
    ---

    """
    queryset = Patient.objects.select_all()
    permission_classes = [CareDoctorReadOnly]  # owner readonly
    serializer_class = PatientDetailSerializer
    lookup_field = 'pk'


class PrescriptionCreate(InputValueSupporter, CreateAPIView):
    """
    소견서 작성
    ---

    """
    queryset = Prescription.objects.select_all().prefetch_doctor_file()  # .defer_option_fields()
    permission_classes = [IsDoctor]
    serializer_class = PrescriptionCreateSerializer

    fields_to_display = 'patient', 'status'


class PrescriptionDetail(RetrieveUpdateAPIView):
    """
    소견서 세부 정보
    ---

    """
    queryset = Prescription.objects.select_all()
    permission_classes = [IsOwner]  # only owner
    serializer_class = PrescriptionDetailSerializer
    lookup_field = 'pk'


# # 보류
# class DoctorFileUpload(InputValueSupporter, CreateAPIView):
#     queryset = DoctorFile.objects.select_all()
#     permission_classes = []  # only doctor
#     serializer_class = DoctorFileUploadSerializer
#     lookup_field = 'pk'
#     fields_to_display = 'prescription'


# # 보류
# class DoctorFileDetail(RetrieveUpdateAPIView):
#     queryset = DoctorFile.objects.select_all()
#     permission_classes = []  # only owner
#     serializer_class = DoctorFlieRetrieveSerializer
#     lookup_field = 'id'


class DoctorFileDelete(DestroyAPIView):
    """
    의사가 올린 파일 삭제
    """
    pass


# # 보류
# class PatientFileDetail(RetrieveAPIView):
#     queryset = PatientFile.objects.select_all()
#     permission_classes = []
#     serializer_class = PatientFlieRetrieveSerializer
#     lookup_field = 'id'


class FilePrescriptionDetail(RetrieveUpdateAPIView):
    """
    환자가 업로드 해야 할 일정에 대한 세부 정보 접근 및 수정
    ---

    """
    queryset = FilePrescription.objects.all()
    permission_classes = [IsOwner]  # only owner
    serializer_class = FilePrescriptionDetailSerializer
    lookup_field = 'pk'


# patient
class DoctorProfileForPatient(RetrieveAPIView):
    """
    의사의 프로필 접근(환자용)
    ---

    """
    queryset = Doctor.objects.select_all()
    permission_classes = []  # owner readonly
    serializer_class = DoctorDetailSerializer
    lookup_field = 'pk'


class PatientProfileForPatient(RetrieveUpdateAPIView):
    """
    환자의 프로필 접근 및 수정(환자용)

    """
    queryset = Patient.objects.select_all()
    permission_classes = []  # onwer readonly
    serializer_class = PatientDetailSerializer
    lookup_field = 'pk'


class PatientFileUpload(CreateAPIView):  # add InputValueSupporter
    """
    환자가 측정한 파일 업로드(환자용)
    ---

    """
    queryset = PatientFile.objects.select_all()
    permission_classes = [IsPatient]
    parser_classes = (FileUploadParser,)

    serializer_class = PatientFileUploadSerializer


class PatientFileDetailForPatient(RetrieveUpdateAPIView):
    """
    환자가 올린 파일 세부정보 및 수정(환자용)
    ---

    """
    queryset = PatientFile.objects.select_all()
    permission_classes = [IsPatient]
    serializer_class = PatientFlieRetrieveSerializer


class PatientFileDelete(DestroyAPIView):
    """
    환자가 올린 파일 삭제(환자용)
    ---

    """
    # IsSuperUser: hard delete
    # IsOwner: shallow delete
    pass
