from typing import TYPE_CHECKING

from rest_framework import serializers

from accounts.api.serializers import OriginalDoctorSerializer, \
    OriginalPatientSerializer
from core.api.core_serializers import (CoreDoctorSerializer,
                                       CorePatientSerializer,
                                       CorePrescriptionSerializer,
                                       CoreFilePrescriptionSerializer,
                                       CoreDoctorFileSerializer,
                                       CorePatientFileSerializer,
                                       CorePrescriptionListSerializer, CoreFilePrescriptionListSerializer)
from core.api.fields import FilePrescriptionFields, PrescriptionFields, PatientFields
from prescriptions.models import FilePrescription

if TYPE_CHECKING:
    from accounts.models import Patient

"""
Doctor Serializer
"""


# 0: 의사 메인페이지(의사 정보 및 담당 환자 리스트)
class DoctorNestedPatientSerializer(CoreDoctorSerializer):
    patients = CorePatientSerializer(many=True)

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


class PatientWithDoctorSerializer(OriginalPatientSerializer):  # Patient<pk>, doctor
    doctor = OriginalDoctorSerializer()

    class Meta(OriginalPatientSerializer.Meta):
        fields = OriginalPatientSerializer.Meta.fields


class PrescriptionListForPatientSerializer(CorePrescriptionListSerializer):  # prescription list
    core_url = serializers.HyperlinkedIdentityField(
        view_name='core-api:patients:prescription-detail',
        lookup_field='pk'
    )

    class Meta(CorePrescriptionListSerializer.Meta):
        fields = PrescriptionFields.list_field + ('core_url',)


class FilePrescriptionsForPatientSerializer(CoreFilePrescriptionSerializer):  # upload schedules
    class Meta(CoreFilePrescriptionSerializer.Meta):
        fields = FilePrescriptionFields.list_field


class PatientMainSerializer(PatientWithDoctorSerializer):
    prescriptions = PrescriptionListForPatientSerializer(many=True)
    upload_schedules = serializers.SerializerMethodField()

    class Meta(PatientWithDoctorSerializer.Meta):
        fields = PatientFields.detail_field + ('prescriptions', 'upload_schedules')

    def get_upload_schedules(self, instance: 'Patient'):
        queryset = FilePrescription.objects. \
            filter(prescription_id=instance.latest_prescription_id).only_list()
        serializer_context = {'request': self.context['request']}
        file_prescriptions = FilePrescriptionsForPatientSerializer(queryset, many=True, context=serializer_context)
        return file_prescriptions.data
