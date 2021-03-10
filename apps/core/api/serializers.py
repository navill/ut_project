from typing import TYPE_CHECKING

from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from accounts.api.serializers import DoctorDetailSerializer, PatientDetailSerializer
from accounts.models import Patient, Doctor
from core.api.core_serializers import (CoreDoctorDetailSerializer,
                                       CoreFilePrescriptionSerializer,
                                       CoreDoctorFileSerializer,
                                       CorePatientFileSerializer,
                                       CorePrescriptionListSerializer, CoreFilePrescriptionListSerializer,
                                       CorePrescriptionDetailSerializer, CorePatientDetailSerializer,
                                       CorePatientListSerializer)
from core.api.fields import FilePrescriptionFields, PrescriptionFields, PatientFields, DoctorFields
from prescriptions.api.serializers import PrescriptionDetailSerializer
from prescriptions.models import FilePrescription, Prescription

"""
Doctor Serializer
"""


class PrescriptionWithDoctorFileSerializer(CorePrescriptionDetailSerializer):
    doctor_files = CoreDoctorFileSerializer(many=True, help_text='의사가 올린 파일 정보')

    class Meta(CorePrescriptionDetailSerializer.Meta):
        fields = CorePrescriptionDetailSerializer.Meta.fields + ['doctor_files']


# 0: 의사 메인페이지(의사 정보 및 담당 환자 리스트)
class DoctorWithPatientSerializer(serializers.ModelSerializer):
    patients = CorePatientListSerializer(many=True, help_text='담당 환자 리스트')

    class Meta:
        model = Doctor
        fields = DoctorFields.detail_field + ['patients']


# 1: 의사가 작성한 환자의 소견서 리스트 + 소견서에 업로드된 파일
class PatientWithPrescriptionSerializer(PatientDetailSerializer):
    prescriptions = CorePrescriptionListSerializer(many=True, help_text='환자의 소견서 리스트')

    class Meta:
        model = Patient
        fields = PatientFields.detail_field + ['prescriptions']


# 2: 소견서에 연결된 중계 모델(FilePrescription)에 업로드된 환자의 파일 정보
class PrescriptionNestedFilePrescriptionSerializer(PrescriptionWithDoctorFileSerializer):
    file_prescriptions = CoreFilePrescriptionListSerializer(many=True)

    class Meta(PrescriptionWithDoctorFileSerializer.Meta):
        fields = PrescriptionWithDoctorFileSerializer.Meta.fields + ['file_prescriptions']


# 3  /file-prescription/<int:pk>/patient-files
class FilePrescriptionNestedPatientFileSerializer(CoreFilePrescriptionSerializer):
    prescription = PrescriptionWithDoctorFileSerializer(read_only=True)
    patient_files = CorePatientFileSerializer(many=True, read_only=True)

    class Meta(CoreFilePrescriptionSerializer.Meta):
        fields = CoreFilePrescriptionSerializer.Meta.fields + ['prescription', 'patient_files']


# 4 /histroies/new-uploaded-file
class UploadedPatientFileHistorySerializer(CoreFilePrescriptionListSerializer):
    class Meta(CoreFilePrescriptionListSerializer.Meta):
        fields = CoreFilePrescriptionListSerializer.Meta.fields


# 5 /histories/expired-upload-date
class ExpiredFilePrescriptionHistorySerializer(CoreFilePrescriptionListSerializer):
    pass


"""
Patient Serializer
"""


class PatientWithDoctorSerializer(PatientDetailSerializer):  # Patient<pk>, doctor
    doctor = DoctorDetailSerializer(help_text='담당 의사 정보')

    class Meta(PatientDetailSerializer.Meta):
        fields = PatientDetailSerializer.Meta.fields


class PrescriptionListForPatientSerializer(CorePrescriptionListSerializer):  # prescription list
    core_url = serializers.HyperlinkedIdentityField(
        view_name='core-api:patients:prescription-detail',
        lookup_field='pk'
    )

    class Meta(CorePrescriptionListSerializer.Meta):
        fields = PrescriptionFields.list_field + ['core_url']


class FilePrescriptionsForPatientSerializer(CoreFilePrescriptionSerializer):  # upload schedules
    class Meta(CoreFilePrescriptionSerializer.Meta):
        fields = FilePrescriptionFields.list_field


class PatientMainSerializer(PatientWithDoctorSerializer):
    prescriptions = PrescriptionListForPatientSerializer(many=True, help_text='의사가 작성한 환자의 소견서 리스트')
    upload_schedules = serializers.SerializerMethodField(help_text='업로드 일정 리스트')

    class Meta(PatientWithDoctorSerializer.Meta):
        fields = PatientFields.detail_field + ['prescriptions', 'upload_schedules']

    @swagger_serializer_method(serializer_or_field=FilePrescriptionsForPatientSerializer)
    def get_upload_schedules(self, instance: 'Patient'):
        queryset = FilePrescription.objects. \
            filter(prescription_id=instance.latest_prescription_id).only_list()
        serializer_context = {'request': self.context['request']}
        file_prescriptions = FilePrescriptionsForPatientSerializer(queryset, many=True, context=serializer_context,
                                                                   help_text='파일 업로드 일정')
        return file_prescriptions.data
