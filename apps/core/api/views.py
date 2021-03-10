from django.db.models import Prefetch
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import RetrieveAPIView, ListAPIView, RetrieveUpdateAPIView, CreateAPIView, DestroyAPIView
from rest_framework.parsers import FileUploadParser

from accounts.api.permissions import IsDoctor, IsOwner, IsPatient, CareDoctorReadOnly
from accounts.api.serializers import DoctorDetailSerializer, PatientDetailSerializer
from accounts.models import Doctor, Patient
from core import docs
from core.api.serializers import (DoctorWithPatientSerializer,
                                  PatientWithPrescriptionSerializer,
                                  PrescriptionNestedFilePrescriptionSerializer,
                                  FilePrescriptionNestedPatientFileSerializer,
                                  ExpiredFilePrescriptionHistorySerializer,
                                  UploadedPatientFileHistorySerializer,
                                  PatientWithDoctorSerializer,
                                  PatientMainSerializer,
                                  PrescriptionWithDoctorFileSerializer,
                                  PrescriptionListForPatientSerializer,
                                  )
from files.api.serializers import PatientFlieRetrieveSerializer, PatientFileUploadSerializer
from files.models import PatientFile
from prescriptions.api.mixins import HistoryMixin
from prescriptions.api.serializers import PrescriptionCreateSerializer, \
    PrescriptionDetailSerializer, FilePrescriptionDetailSerializer
from prescriptions.models import Prescription, FilePrescription


# doctor - main
class DoctorWithPatients(RetrieveAPIView):
    queryset = Doctor.objects.select_all()
    permission_classes = [IsOwner]
    serializer_class = DoctorWithPatientSerializer
    lookup_field = 'pk'

    @swagger_auto_schema(**docs.doctor_with_patients)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class PatientWithPrescriptions(RetrieveAPIView):
    queryset = Patient.objects.select_all().prefetch_prescription_with_writer()
    permission_classes = [IsDoctor]
    serializer_class = PatientWithPrescriptionSerializer
    lookup_field = 'pk'

    @swagger_auto_schema(**docs.patient_with_prescriptions)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class PrescriptionWithFilePrescriptions(RetrieveAPIView):
    queryset = Prescription.objects.select_all()
    permission_classes = [IsDoctor]
    serializer_class = PrescriptionNestedFilePrescriptionSerializer
    lookup_field = 'pk'

    @swagger_auto_schema(**docs.prescription_with_file_prescription)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class FilePrescriptionWithPatientFiles(RetrieveAPIView):
    queryset = FilePrescription.objects.nested_all()
    permission_classes = [IsOwner]
    serializer_class = FilePrescriptionNestedPatientFileSerializer
    lookup_field = 'pk'

    @swagger_auto_schema(**docs.file_prescription_with_patient_file)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


# todo: 아래의 두 history를 하나의 endpoint에서 처리(분기는 query parameter로)할 수 있을듯
# doctor - history
class UploadedPatientFileHistory(HistoryMixin, ListAPIView):
    queryset = FilePrescription.objects.nested_all().filter_new_uploaded_file()
    permission_classes = [IsDoctor]
    serializer_class = UploadedPatientFileHistorySerializer

    @swagger_auto_schema(**docs.uploaded_patient_file_history)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ExpiredFilePrescriptionHistory(HistoryMixin, ListAPIView):
    queryset = FilePrescription.objects.nested_all().filter_upload_date_expired()
    permission_classes = [IsDoctor]
    serializer_class = ExpiredFilePrescriptionHistorySerializer

    @swagger_auto_schema(**docs.expired_file_prescription_history)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class PatientWithDoctor(RetrieveAPIView):  # 환자 첫 페이지 - 담당 의사 정보 포함
    """
    [DETAIL] 담당 의사 정보를 환자의 정보 페이지

    ---
    - 기능: 환자의 정보와 담당 의사 정보를 표시
    - 권한: IsPatient(환자 계정) -> IsOwner로 변경할 예정
    - 내용
        - 환자 세부 정보
        - doctor: 담당 의사 세부 정보
    """
    queryset = Patient.objects.select_all()
    # permission_classes = [IsPatient]
    permission_classes = []
    serializer_class = PatientWithDoctorSerializer
    lookup_field = 'pk'


class PrescriptionListForPatient(ListAPIView):  # 환자와 관련된 소견서 + 의사 파일 + FilePrescriptionList
    """
    [LIST] 해당 환자에 대해 작성된 소견서 리스트

    ---
    - 기능: 로그인한 환자의 소견서 리스트 표시
    - 권한: IsOwner

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
    [DETAIL] 환자가 접근할 수 있는 소견서의 세부 정보

    ---
    - 기능: 소견서 리스트에서 특정 소견서를 선택할 경우 해당 소견서의 세부 내용 출력
    - 권한: RelatedPatientReadOnly(객체와 관계된 환자일 경우 읽기 가능)
    - 내용
        - 소견서 세부 내용
        - doctor_files: 의사가 올린 파일 정보
    """
    queryset = Prescription.objects.select_all()
    permission_classes = []
    # permission_classes = [RelatedPatientReadOnly]
    serializer_class = PrescriptionWithDoctorFileSerializer
    lookup_field = 'pk'


class FilePrescriptionListForPatient(RetrieveAPIView):  # Detail FilePrescription + PatietFile
    """
    [LIST] 환자가 접근할 수 있는 파일 업로드 일정 리스트

    ---
    - 기능: 의사가 생성한 스케줄(파일 업로드 일정)을 확인할 때 사용
    - 권한: RelatedPatientReadOnly(객체와 관계된 환자일 경우 읽기 가능)
    - 내용
        - 소견서 내용
        - doctor_files: 의사가 소견서를 작성하면서 함께 올린 파일 정보
        - file_prescriptions: 의사가 소견서를 작성하면서 지정한 파일 업로드 스케줄
    """
    queryset = Prescription.objects.select_all()
    # permission_classes = [IsPatient]
    permission_classes = []
    serializer_class = PrescriptionNestedFilePrescriptionSerializer
    lookup_field = 'pk'


class FilePrescriptionDetailForPatient(RetrieveAPIView):
    """
    [DETAIL] 환자가 접근할 수 있는 파일 업로드 일정의 세부 정보

    ---
    - 기능: 업로드 일정의 세부 정보 표시
        - 환자가 올린 파일, 의사가 환자의 파일에 대해 작성한 소견서도 포함
    - 권한: RelatedPatientReadOnly
    - 내용
        - 스케줄 및 상태 정보
        - prescription: 대면시 작성된 소견서
            - doctor_files: 의사가 업로드한 파일 정보
        - patient_files: 환자가 업로드한 파일 정보
    """
    queryset = FilePrescription.objects.select_all()
    permission_classes = []
    serializer_class = FilePrescriptionNestedPatientFileSerializer
    lookup_field = 'pk'


class PatientMain(RetrieveAPIView):
    """
    [DETAIL] 환자용 메인 페이지

    ---
    - 기능: 환자 계정으로 로그인 시 처음 보여질 내용 표시
    - 권한: IsOnwer
    - 내용
        - 환자 정보
        - doctor: 담당 의사 정보
        - prescriptions: 환자의 소견서 리스트
        - upload_schedules: 업로드 일정
    """
    queryset = Patient.objects.select_all(). \
        prefetch_prescription(Prefetch('prescriptions', queryset=Prescription.objects.select_all().only_list())). \
        with_latest_prescription(). \
        only_detail('updated_at')
    permission_classes = []
    serializer_class = PatientMainSerializer
    lookup_field = 'pk'
    path_type_user = openapi.TYPE_INTEGER


# patient - history
class ChecekdFilePrescription(ListAPIView):  # 환자가 올린 파일을 의사가 확인(checked=True)한 리스트
    """
    [LIST] 환자가 업로드한 파일을 의사가 확인했을 경우 표시될 리스트 -> 개발 예정
    """
    pass


class DoctorProfile(RetrieveUpdateAPIView):
    """
    [DETAIL, UPDATE] 의사의 프로필 접근 및 수정

    ---
    - 기능: 의사의 프로필 접근 및 수정
    - 권한: IsOwner
    """
    queryset = Doctor.objects.select_all()
    permission_classes = [IsOwner]  # owner readonly
    serializer_class = DoctorDetailSerializer
    lookup_field = 'pk'
    path_type_user = openapi.TYPE_INTEGER


class PatientProfile(RetrieveAPIView):
    """
    [DETAIL] 환자의 프로필 접근(의사용)

    ---
    - 기능: 담당하고 있는 환자의 프로필 접근
    - 권한: CareDoctorReadOnly(담당 의사일 경우 읽기 가능)
    """
    queryset = Patient.objects.select_all()
    permission_classes = [CareDoctorReadOnly]  # owner readonly
    serializer_class = PatientDetailSerializer
    lookup_field = 'pk'
    path_type_user = openapi.TYPE_INTEGER


class PrescriptionCreate(CreateAPIView):
    """
    [CREATE] 소견서 작성

    ---
    - 기능: 환자에 대한 소견서 작성 및 파일 업로드(의사용), 환자의 파일 업로드 스케줄을 지정
    - 권한: IsDoctor(의사 계정)
    - 내용
        - 소견서 내용
        - 업로드 스케줄(start_date~end_date)
        - doctor_upload_files: 의사가 업로드할 파일 필드(directory path)
    """
    queryset = Prescription.objects.select_all().prefetch_doctor_file()  # .defer_option_fields()
    permission_classes = [IsDoctor]
    serializer_class = PrescriptionCreateSerializer


class PrescriptionDetail(RetrieveUpdateAPIView):
    """
    [DETAIL, UPDATE] 소견서 세부 정보

    ---
    - 기능: 소견서의 세부 정보를 확인하거나 수정 작업
    - 권한: IsOwner(작성자 - 접근&수정)
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
    [DELETE] 의사가 올린 파일 삭제
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
    [DETAIL, UPDATE] 파일 업로드 일정에 대한 세부 정보 접근 및 수정

    ---
    - 기능: 파일 업로드 스케줄 관련 세부 정보 표시 및 정보 수정
    - 권한: IsOwner(스케줄을 작성한 의사 계정)
    """
    queryset = FilePrescription.objects.all()
    permission_classes = [IsOwner]  # only owner
    serializer_class = FilePrescriptionDetailSerializer
    lookup_field = 'pk'


# patient
class DoctorProfileForPatient(RetrieveAPIView):
    """
    [DETAIL] 의사의 프로필 접근(환자용)

    ---
    - 기능: 담당 의사의 프로필 정보 표시
    - 권한: IsPatient
    """
    queryset = Doctor.objects.select_all()
    permission_classes = []
    serializer_class = DoctorDetailSerializer
    lookup_field = 'pk'
    path_type_user = openapi.TYPE_INTEGER

    def get_object(self):
        obj = super().get_object()
        if obj.patients.filter(user_id=self.request.user.id).exists():
            return obj
        else:
            raise Exception('??')


class PatientProfileForPatient(RetrieveUpdateAPIView):
    """
    [DETAIL, UPDATE]환자의 프로필 접근 및 수정(환자용)

    ---
    - 기능: 환자 본인 계정의 정보 표시 및 수정
    - 권한: IsOwner
    """
    queryset = Patient.objects.select_all()
    permission_classes = []  # onwer readonly
    serializer_class = PatientDetailSerializer
    lookup_field = 'pk'
    path_type_user = openapi.TYPE_INTEGER


class PatientFileUpload(CreateAPIView):
    """
    [CREATE]파일 업로드(환자용)

    ---
    - 기능: 환자용 파일 객체 생성
    - 권한: IsPatient
    """
    queryset = PatientFile.objects.select_all()
    permission_classes = [IsPatient]
    parser_classes = (FileUploadParser,)
    serializer_class = PatientFileUploadSerializer


class PatientFileDetailForPatient(RetrieveUpdateAPIView):
    """
    [DETAIL, UPDATE]환자가 올린 파일 세부정보 접근 및 수정(환자용)

    ---
    - 기능: 업로드한 파일의 세부 정보 표시 및 수정
    - 권한: IsOwner
    """
    queryset = PatientFile.objects.select_all()
    permission_classes = [IsPatient]
    serializer_class = PatientFlieRetrieveSerializer


class PatientFileDelete(DestroyAPIView):
    """
    [DELETE] 환자가 올린 파일 삭제(환자용)

    ---

    """
    # IsSuperUser: hard delete
    # IsOwner: shallow delete
    pass
