from typing import TYPE_CHECKING

from django.db.models import Prefetch, F, QuerySet
from rest_framework import serializers

from accounts.api.serializers import PatientSerializer, DoctorSerializer
from accounts.models import Patient
from core.api.core_serializers import (CoreDoctorSerializer,
                                       CorePatientSerializer,
                                       CorePrescriptionSerializer,
                                       CoreFilePrescriptionSerializer,
                                       CoreDoctorFileSerializer,
                                       CorePatientFileSerializer, CoreRawPatientSerializer)
from prescriptions.api.serializers import FilePrescriptionSerializer
from prescriptions.models import Prescription, FilePrescription

if TYPE_CHECKING:
    pass

"""
Doctor Serializer
"""


# 0: 의사 메인페이지(의사 정보 및 담당 환자 리스트)
class DoctorNestedPatientSerializer(CoreDoctorSerializer):
    patients = CoreRawPatientSerializer(many=True)

    class Meta(CoreDoctorSerializer.Meta):
        fields = CoreDoctorSerializer.Meta.fields + ['patients']


# 1: 의사가 작성한 환자의 소견서 리스트 + 소견서에 업로드된 파일
class PatientNestedPrescriptionSerializer(CorePatientSerializer):
    prescriptions = CorePrescriptionSerializer(many=True)

    class Meta(CorePatientSerializer.Meta):
        fields = CorePatientSerializer.Meta.fields + ['prescriptions']


class PrescriptionNestedDoctorFileSerializer(CorePrescriptionSerializer):
    doctor_files = CoreDoctorFileSerializer(many=True)

    class Meta(CorePrescriptionSerializer.Meta):
        fields = CorePrescriptionSerializer.Meta.fields + ['doctor_files']


# 2: 소견서에 연결된 중계 모델(FilePrescription)에 업로드된 환자의 파일 정보
class PrescriptionNestedFilePrescriptionSerializer(PrescriptionNestedDoctorFileSerializer):
    file_prescriptions = CoreFilePrescriptionSerializer(many=True)

    class Meta(PrescriptionNestedDoctorFileSerializer.Meta):
        fields = PrescriptionNestedDoctorFileSerializer.Meta.fields + ['file_prescriptions']


# 3  /file-prescription/<int:pk>/patient-files
class FilePrescriptionNestedPatientFileSerializer(CoreFilePrescriptionSerializer):
    prescription = PrescriptionNestedDoctorFileSerializer()
    patient_files = CorePatientFileSerializer(many=True)

    class Meta(CoreFilePrescriptionSerializer.Meta):
        fields = CoreFilePrescriptionSerializer.Meta.fields + ['prescription', 'patient_files']


# 4 /histroies/new-uploaded-file
class UploadedPatientFileHistorySerializer(CoreFilePrescriptionSerializer):
    pass


# 5 /histories/expired-upload-date
class ExpiredFilePrescriptionHistorySerializer(CoreFilePrescriptionSerializer):
    pass


"""
Patient Serializer
"""


class PatientWithDoctorSerializer(PatientSerializer):  # Patient<pk>, doctor
    doctor = DoctorSerializer()

    class Meta(PatientSerializer.Meta):
        fields = PatientSerializer.Meta.fields


class PrescriptionsRelatedPatientSerializer(CorePrescriptionSerializer):  # prescription list
    class Meta(CorePrescriptionSerializer.Meta):
        fields = CorePrescriptionSerializer.Meta.fields


class FilePrescriptionsSerializer(CoreFilePrescriptionSerializer):  # file upload schedules
    class Meta(CoreFilePrescriptionSerializer.Meta):
        fields = CoreFilePrescriptionSerializer.Meta.fields


class PatientMainSerializer(PatientWithDoctorSerializer):
    # in view
    # queryset = Patient.objects.select_related('prescriptions','file_prescriptions', 'doctor')

    prescriptions = PrescriptionsRelatedPatientSerializer(many=True)
    upload_schedule = serializers.SerializerMethodField()

    class Meta(PatientWithDoctorSerializer.Meta):
        fields = PatientWithDoctorSerializer.Meta.fields + ['prescriptions', 'upload_schedule']

    def get_upload_schedule(self, instance):
        # self.context['request'].user
        prescription = instance.prescriptions.last()
        # print(prescription_id)
        # 환자의 마지막 prescription에 등록된 file prescriptions
        file_prescriptions = FilePrescription.objects.filter(prescription_id=prescription.id)
        return file_prescriptions.values()
