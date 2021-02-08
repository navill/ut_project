from rest_framework import serializers

from accounts.api.serializers import (DoctorSerializer,
                                      PatientSerializer,
                                      RawDoctorSerializer,
                                      RawPatientSerializer,
                                      OriginalDoctorSerializer,
                                      OriginalPatientSerializer)
from core.api.fields import DoctorFields, PatientFields, PrescriptionFields, FilePrescriptionFields
from files.api.serializers import PatientFileSerializer, DoctorFileSerializer
from hospitals.api.serializers import MajorListSerializer
from prescriptions.api.serializers import (PrescriptionSerializer,
                                           FilePrescriptionSerializer,
                                           OriginalPrescriptionSerializer,
                                           OriginalFilePrescriptionSerializer)


class CoreRawDoctorSerializer(RawDoctorSerializer):
    class Meta(RawDoctorSerializer.Meta):
        fields = RawDoctorSerializer.Meta.fields


class CoreDoctorSerializer(DoctorSerializer):
    detail_url = serializers.HyperlinkedIdentityField(
        view_name='accounts:doctor-detail-update',
        lookup_field='pk'
    )

    class Meta(DoctorSerializer.Meta):
        fields = DoctorSerializer.Meta.fields + ['detail_url']


class CoreRawPatientSerializer(RawPatientSerializer):
    class Meta(RawPatientSerializer.Meta):
        fields = RawPatientSerializer.Meta.fields


class CorePatientSerializer(PatientSerializer):
    core_url = serializers.HyperlinkedIdentityField(
        view_name='core-api:doctors:prescription-list',
        lookup_field='pk'
    )
    detail_url = serializers.HyperlinkedIdentityField(
        view_name='accounts:patient-detail-update',
        lookup_field='pk'
    )

    class Meta(PatientSerializer.Meta):
        fields = PatientSerializer.Meta.fields + ['detail_url', 'core_url']


class CoreDoctorFileSerializer(DoctorFileSerializer):
    # doctor detail_(update)url
    # doctor delete_url

    class Meta(DoctorFileSerializer.Meta):
        fields = DoctorFileSerializer.Meta.fields


class CorePatientFileSerializer(PatientFileSerializer):
    # patient detail(update)_url
    # patient delete_url

    class Meta(PatientFileSerializer.Meta):
        fields = PatientFileSerializer.Meta.fields


class CorePrescriptionSerializer(PrescriptionSerializer):
    # prescription detail_(update)url
    core_url = serializers.HyperlinkedIdentityField(
        view_name='core-api:prescription-detail',
        lookup_field='pk'
    )

    class Meta(PrescriptionSerializer.Meta):
        fields = PrescriptionSerializer.Meta.fields + ['core_url']


class CoreFilePrescriptionSerializer(FilePrescriptionSerializer):
    # file prescription detail_(update)url
    core_url = serializers.HyperlinkedIdentityField(
        view_name='core-api:file-prescription-detail',
        lookup_field='pk'
    )

    class Meta(FilePrescriptionSerializer.Meta):
        fields = FilePrescriptionSerializer.Meta.fields + ['core_url']


# 아직 사용 x
class CoreDoctorListSerializer(OriginalDoctorSerializer):
    major = MajorListSerializer()

    class Meta(OriginalDoctorSerializer.Meta):
        fields = DoctorFields.list_field


# 의사 메인페이지
# - 환자 리스트 -> core prescriptions
class CorePatientListSerializer(OriginalPatientSerializer):
    class Meta(OriginalPatientSerializer.Meta):
        fields = PatientFields.list_field


# 의사 메인 페이지
# - 선택된 환자의 소견서 리스트 (소견서 선택-> file prescription list)
# 환자 메인 페이지
# - 로그인한 환자의 소견서 리스트 (소견서 선택 -> file prescription list)
class CorePrescriptionListSerializer(OriginalPrescriptionSerializer):
    core_url = serializers.HyperlinkedIdentityField(
        view_name='core-api:prescription-detail',
        lookup_field='pk'
    )
    writer = CoreDoctorListSerializer()

    class Meta(OriginalPrescriptionSerializer.Meta):
        fields = PrescriptionFields.list_field + ('core_url',)


# 의사 메인 페이지
# - 선택된 소견서의 FilePrescription 리스트 (FilePrescription 선택 -> PatientFile 리스트)
# 환자 메인 페이지
# - 선택된 소견서의 FilePrescription 리스트 (FilePrescription 선택 -> PatientFile 리스트)
# - 환자가 파일을 업로드 해야할 FilePrescription 리스트 (FilePrescription 선택 -> PatientFile 업로드 페이지 or detail 페이지)
class CoreFilePrescriptionListSerializer(OriginalFilePrescriptionSerializer):
    class Meta(OriginalFilePrescriptionSerializer.Meta):
        fields = FilePrescriptionFields.list_field
