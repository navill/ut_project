from rest_framework import serializers

from accounts.api.serializers import DoctorDetailSerializer, PatientDetailSerializer, DoctorListSerializer, \
    PatientListSerializer
from files.api.serializers import PatientFileSerializer, DoctorFileSerializer
from prescriptions.api.serializers import (PrescriptionListSerializer,
                                           PrescriptionDetailSerializer, FilePrescriptionListSerializer,
                                           FilePrescriptionDetailSerializer, PrescriptionCreateSerializer)


class CoreDoctorListSerializer(DoctorListSerializer):
    pass


class CoreDoctorDetailSerializer(DoctorDetailSerializer):
    profile_url = serializers.HyperlinkedIdentityField(
        view_name='core-api:doctors:doctor-profile',
        lookup_field='pk'
    )

    class Meta(DoctorDetailSerializer.Meta):
        fields = DoctorDetailSerializer.Meta.fields + ['profile_url']


class CorePatientListSerializer(PatientListSerializer):
    class Meta(PatientListSerializer.Meta):
        fields = PatientListSerializer.Meta.fields


class CorePatientDetailSerializer(PatientDetailSerializer):
    prescription_url = serializers.HyperlinkedIdentityField(
        view_name='core-api:doctors:prescription-list',
        lookup_field='pk'
    )
    profile_url = serializers.HyperlinkedIdentityField(
        view_name='core-api:doctors:patient-profile',
        lookup_field='pk'
    )

    class Meta(PatientDetailSerializer.Meta):
        fields = PatientDetailSerializer.Meta.fields + ['profile_url', 'prescription_url']


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


class CorePrescriptionListSerializer(PrescriptionListSerializer):
    # prescription detail_(update)url
    prescription_detail_url = serializers.HyperlinkedIdentityField(
        view_name='core-api:doctors:prescription-file',
        lookup_field='pk'
    )

    class Meta(PrescriptionListSerializer.Meta):
        fields = PrescriptionListSerializer.Meta.fields + ['prescription_detail_url']


class CorePrescriptionDetailSerializer(PrescriptionDetailSerializer):
    class Meta(PrescriptionDetailSerializer.Meta):
        fields = PrescriptionDetailSerializer.Meta.fields  # + ['prescription_with_file_url']


class CorePrescriptionCreateSrializer(PrescriptionCreateSerializer):
    class Meta(PrescriptionCreateSerializer.Meta):
        fields = PrescriptionCreateSerializer.Meta.fields


class CoreFilePrescriptionSerializer(FilePrescriptionDetailSerializer):
    # file prescription detail_(update)url
    core_url = serializers.HyperlinkedIdentityField(
        view_name='core-api:doctors:file-prescription-with-patient-file',
        lookup_field='pk'
    )

    class Meta(FilePrescriptionDetailSerializer.Meta):
        fields = FilePrescriptionDetailSerializer.Meta.fields + ['core_url']


# # 아직 사용 x
# class CoreDoctorListSerializer(DoctorDetailSerializer):
#     major = MajorListSerializer()
#
#     class Meta(DoctorDetailSerializer.Meta):
#         fields = DoctorFields.list_field
#
#
# # 의사 메인페이지
# # - 환자 리스트 -> core prescriptions
# class CorePatientListSerializer(PatientDetailSerializer):
#     class Meta(PatientDetailSerializer.Meta):
#         fields = PatientFields.list_field


# 의사 메인 페이지
# - 선택된 환자의 소견서 리스트 (소견서 선택-> file prescription list)
# 환자 메인 페이지
# - 로그인한 환자의 소견서 리스트 (소견서 선택 -> file prescription list)
# class CorePrescriptionListSerializer(OriginalPrescriptionSerializer):
#     core_url = serializers.HyperlinkedIdentityField(
#         view_name='core-api:prescription-detail',
#         lookup_field='pk'
#     )
#     writer = CoreDoctorListSerializer()
#
#     class Meta(OriginalPrescriptionSerializer.Meta):
#         fields = PrescriptionFields.list_field + ['core_url']


# 의사 메인 페이지
# - 선택된 소견서의 FilePrescription 리스트 (FilePrescription 선택 -> PatientFile 리스트)
# 환자 메인 페이지
# - 선택된 소견서의 FilePrescription 리스트 (FilePrescription 선택 -> PatientFile 리스트)
# - 환자가 파일을 업로드 해야할 FilePrescription 리스트 (FilePrescription 선택 -> PatientFile 업로드 페이지 or detail 페이지)
class CoreFilePrescriptionListSerializer(FilePrescriptionListSerializer):
    file_prescription_detail_url = serializers.HyperlinkedIdentityField(
        view_name='core-api:doctors:file-prescription-with-patient-file',
        lookup_field='pk'
    )

    class Meta(FilePrescriptionListSerializer.Meta):
        fields = FilePrescriptionListSerializer.Meta.fields + ['file_prescription_detail_url']


class CoreFilePrescriptionDetailSerializer(FilePrescriptionDetailSerializer):
    # add url

    class Meta(FilePrescriptionDetailSerializer.Meta):
        fields = FilePrescriptionDetailSerializer.Meta.fields
