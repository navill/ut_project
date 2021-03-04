from rest_framework.generics import RetrieveUpdateAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.parsers import MultiPartParser, FileUploadParser

from accounts.api.permissions import IsDoctor, IsOwner, RelatedPatientReadOnly, IsPatient
from config.utils.api_utils import InputValueSupporter
from prescriptions.api.serializers import (
    PrescriptionCreateSerializer,
    FilePrescriptionListSerializer,
    FilePrescriptionCreateSerializer,
    NestedPrescriptionSerializer,
    PrescriptionListSerializer,
    PrescriptionDetailSerializer, FilePrescriptionDetailSerializer)
from prescriptions.api.utils import CommonListAPIView
from prescriptions.models import Prescription, FilePrescription


class PrescriptionListAPIView(CommonListAPIView):
    """
    [LIST] 소견서 리스트

    ---
    - 기능: 접속한 계정에 관계된 소견서 리스트 출력
    - 권한: IsDoctor or IsPatient
    """
    queryset = Prescription.objects.select_all().prefetch_doctor_file()  # .defer_option_fields()
    serializer_class = PrescriptionListSerializer
    permission_classes = [IsDoctor | IsPatient]
    lookup_field = 'pk'


class PrescriptionCreateAPIView(CreateAPIView):
    """
    [CREATE] 소견서 작성

    ---
    - 기능: 환자에 대한 소견서를 작성.
        - prescription 생성 시, FilePrescription(환자 파일 업로드 일정), DoctorFile(의사가 올린 파일) 객체도 함께 생성된다.
    - 권한: IsDoctor

    """
    queryset = Prescription.objects.select_all().prefetch_doctor_file()  # .defer_option_fields()
    serializer_class = PrescriptionCreateSerializer
    # permission_classes = [IsDoctor]
    permission_classes = []
    # parser_classes = (FileUploadParser,)

    # fields_to_display = 'patient', 'status'


class PrescriptionRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    """
    [DETAIL, UPDATE] 소견서 세부사항 및 수정

    ---
    - 기능: 작성된 소견서의 세부사항을 확인하거나 수정.
    - 권한: IsOwner or RelatedPatientReadOnly(관계된 환자 계정은 읽기 가능)

    """
    queryset = Prescription.objects.select_all()  # .defer_option_fields()
    serializer_class = PrescriptionDetailSerializer
    permission_classes = [IsOwner | RelatedPatientReadOnly]
    lookup_field = 'pk'

    # def perform_update(self, serializer):
    #     serializer.save()


class FilePrescriptionListAPIView(CommonListAPIView):
    """
    [LIST] FilePrescription 리스트 출력

    ---
    FilePrescription 객체: 소견서 객체(Prescription)와 환자가 업로드한 파일(PatientFile)의 중간 객체
    내용
    ```
        - 소견서 세부 정보
        - 환자의 파일 업로드 여부
        - 의사가 업로드된 파일을 확인했는지 여부 + 파일을 바탕으로 작성된 소견서
        - 기타 정보
    ```

    """
    queryset = FilePrescription.objects.all()
    serializer_class = FilePrescriptionListSerializer
    permission_classes = [IsDoctor | IsPatient]


class FilePrescriptionCreateAPIView(CreateAPIView):
    """
    [CREATE] FilePrescription 객체 생성

    ---
    - 기능: file prescription 객체를 생성하는 end point
        - 보통은 prescription이 생성될 때 자동으로 생성되며, 의도적으로 file prescription 객체를 생성해야할 때 사용
    - 권한: IsDoctor
    """
    queryset = FilePrescription.objects.all()
    serializer_class = FilePrescriptionCreateSerializer
    permission_classes = [IsDoctor]
    parser_classes = (FileUploadParser,)


class FilePrescriptionRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    """
    [DETAIL, UPDATE] FilePrescription 세부 정보 접근 및 수정

    ---
    - 기능: file prescription 객체의 세부 정보 출력
    - 권한: IsOwner(읽기 & 수정) or RelatedPatientReadOnly(관계된 환자는 읽기 가능)
    """
    queryset = FilePrescription.objects.all()
    serializer_class = FilePrescriptionDetailSerializer
    permission_classes = [IsOwner | RelatedPatientReadOnly]
    lookup_field = 'pk'


# class TestPrescriptionAPIView(RetrieveAPIView):
#     queryset = Prescription.objects.nested_all()  # + defer_option_fields()
#     serializer_class = NestedPrescriptionSerializer
#     permission_classes = [IsOwner | RelatedPatientReadOnly]
#     lookup_field = 'pk'
