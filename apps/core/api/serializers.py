from typing import Dict

from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from accounts.api.serializers import DoctorDetailSerializer, PatientDetailSerializer
from accounts.models import Patient, Doctor
from core.api.core_serializers import (CoreFilePrescriptionSerializer,
                                       CoreDoctorFileSerializer,
                                       CorePatientFileSerializer,
                                       CorePrescriptionListSerializer,
                                       CoreFilePrescriptionListSerializer,
                                       CorePrescriptionDetailSerializer,
                                       CorePatientListSerializer)
from core.api.fields import FilePrescriptionFields, PrescriptionFields, PatientFields, DoctorFields
from prescriptions.models import FilePrescription, Prescription

"""
Doctor Serializer
"""


class PrescriptionWithDoctorFileSerializer(CorePrescriptionDetailSerializer):
    doctor_files = CoreDoctorFileSerializer(many=True, source='not_deleted')

    class Meta(CorePrescriptionDetailSerializer.Meta):
        fields = CorePrescriptionDetailSerializer.Meta.fields + ['doctor_files']


# 0: 의사 메인페이지(의사 정보 및 담당 환자 리스트)
class DoctorWithPatientSerializer(serializers.ModelSerializer):
    """
    의사 계정으로 로그인 시 첫 로딩될 데이터를 포함한 serializer
    """
    patients = CorePatientListSerializer(many=True)

    class Meta:
        model = Doctor
        fields = DoctorFields.detail_field + ['patients']


# 1: 의사가 작성한 환자의 소견서 리스트 + 소견서에 업로드된 파일
class PatientWithPrescriptionSerializer(PatientDetailSerializer):
    prescriptions = CorePrescriptionListSerializer(many=True)

    class Meta:
        model = Patient
        fields = PatientFields.detail_field + ['prescriptions']


# 2: 소견서에 연결된 중계 모델(FilePrescription)에 업로드된 환자의 파일 정보
class PrescriptionNestedFilePrescriptionSerializer(CorePrescriptionDetailSerializer):
    doctor_files = CoreDoctorFileSerializer(many=True, source='not_deleted')
    file_prescriptions = CoreFilePrescriptionListSerializer(many=True)

    class Meta(CorePrescriptionDetailSerializer.Meta):
        fields = CorePrescriptionDetailSerializer.Meta.fields + ['doctor_files', 'file_prescriptions']


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
    doctor = DoctorDetailSerializer()

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
    """
    환자 계정으로 로그인 시 첫 로딩될 데이터를 포함한 serializer
    """
    prescriptions = serializers.SerializerMethodField()
    upload_schedules = serializers.SerializerMethodField()

    class Meta(PatientWithDoctorSerializer.Meta):
        fields = PatientFields.detail_field + ['prescriptions', 'upload_schedules']

    @swagger_serializer_method(serializer_or_field=PrescriptionListForPatientSerializer)
    def get_prescriptions(self, instance: 'Patient') -> Dict[str, str]:
        queryset = Prescription.objects.select_all().filter(patient_id=instance.user_id)[:10]
        serializer_context = {'request': self.context['request']}
        prescription_serializer = PrescriptionListForPatientSerializer(instance=queryset, many=True,
                                                                       context=serializer_context)
        return prescription_serializer.data

    @swagger_serializer_method(serializer_or_field=FilePrescriptionsForPatientSerializer)
    def get_upload_schedules(self, instance: 'Patient') -> Dict[str, str]:
        queryset = FilePrescription.objects.filter(
            prescription_id=instance.latest_prescription_id).filter_not_uploaded().only_list().order_by('date')[:10]
        serializer_context = {'request': self.context['request']}
        file_prescriptions = FilePrescriptionsForPatientSerializer(instance=queryset, many=True,
                                                                   context=serializer_context)
        return file_prescriptions.data
