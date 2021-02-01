from typing import TYPE_CHECKING

from core.api.core_serializers import (CoreDoctorSerializer,
                                       CorePatientSerializer,
                                       CorePrescriptionSerializer,
                                       CoreFilePrescriptionSerializer,
                                       CoreDoctorFileSerializer,
                                       CorePatientFileSerializer, CoreRawPatientSerializer)

if TYPE_CHECKING:
    pass

"""
login
[POST]/login
logout
[GET]/logout

doctor main
#0 - [GET]/doctors/<int:pk>/patients
- [GET]/patients
- [GET]/doctors/<int:pk>

#1 - [GET]/patients/<int:patient_id>/prescriptions
- [GET]/patients/<int:pk>
- [GET]/prescriptions

#2 - [GET]/prescription-nested-files/<int:prescription_id>/file-prescriptions
- [GET]/prescriptions/<int:pk>
- [GET]/datafiles/doctor-files
- [GET]/prescriptions/file-pres

#3 - [GET]/file-prescription/<int:pk>/patient-files

#4 - [GET]/histroies/new-uploaded-file

#5 - [GET]/histories/expired-upload-date

Doctor Retrieve & Update
[GET, PUT]/doctors/<int:pk>

DoctorFile Retreive & Update
[GET, PUT]/datafiles/doctor-files/<uuid:pk>

Prescription Retrieve & Update
[GET, PUT]/prescriptions/<int:pk>

FilePrescription Retreive & Update
[GET, PUT]/prescriptions/file-pres/<int:pk>
"""


# 0: 의사 메인페이지(의사 정보 및 담당 환자 리스트)
class DoctorNestedPatientSerializer(CoreDoctorSerializer):
    patients = CoreRawPatientSerializer(many=True)

    class Meta(CoreDoctorSerializer.Meta):
        fields = CoreDoctorSerializer.Meta.fields + ['patients']


##################

# 1: 의사가 작성한 환자의 소견서 리스트 + 소견서에 업로드된 파일
class PatientNestedPrescriptionSerializer(CorePatientSerializer):
    prescriptions = CorePrescriptionSerializer(many=True)

    class Meta(CorePatientSerializer.Meta):
        fields = CorePatientSerializer.Meta.fields + ['prescriptions']


###################

class PrescriptionNestedDoctorFileSerializer(CorePrescriptionSerializer):
    doctor_files = CoreDoctorFileSerializer(many=True)

    class Meta(CorePrescriptionSerializer.Meta):
        fields = CorePrescriptionSerializer.Meta.fields + ['doctor_files']


# 2: 소견서에 연결된 중계 모델(FilePrescription)에 업로드된 환자의 파일 정보
class PrescriptionNestedFilePrescriptionSerializer(PrescriptionNestedDoctorFileSerializer):
    file_prescriptions = CoreFilePrescriptionSerializer(many=True)

    class Meta(PrescriptionNestedDoctorFileSerializer.Meta):
        fields = PrescriptionNestedDoctorFileSerializer.Meta.fields + ['file_prescriptions']


##################

# 3  /file-prescription/<int:pk>/patient-files
class FilePrescriptionNestedPatientFileSerializer(CoreFilePrescriptionSerializer):
    prescription = PrescriptionNestedDoctorFileSerializer()
    patient_files = CorePatientFileSerializer(many=True)

    class Meta(CoreFilePrescriptionSerializer.Meta):
        fields = CoreFilePrescriptionSerializer.Meta.fields + ['prescription', 'patient_files']


##################

# 4 /histroies/new-uploaded-file
class UploadedPatientFileHistorySerializer(CoreFilePrescriptionSerializer):
    pass


##################

# 5 /histories/expired-upload-date
class ExpiredFilePrescriptionHistorySerializer(CoreFilePrescriptionSerializer):
    pass
