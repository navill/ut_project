from typing import Dict, Any, Optional, Type, TYPE_CHECKING, NoReturn

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CurrentUserDefault
from rest_framework.serializers import ListSerializer

from files.models import DoctorFile, PatientFile
from prescriptions.models import Prescription, FilePrescription

if TYPE_CHECKING:
    from django.db.models import QuerySet

User = get_user_model()


class BasedCurrentUserPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self) -> Optional[Type['QuerySet']]:
        request = self.context.get('request', None)
        queryset = super().get_queryset()
        return queryset.filter(user=request.user.id)


class CurrentPatientPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self) -> Optional[Type['QuerySet']]:
        request = self.context.get('request', None)
        queryset = super().get_queryset()
        return queryset.filter(prescription__patient_id=request.user.id)


"""
BaseFile Serializer
"""


class _BaseFileSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(default=False, read_only=True)

    def get_uploader_name(self, instance: User):
        return getattr(instance, 'uploader_patient_name', None) or getattr(instance, 'uploader_doctor_name', None)


"""
DoctorFile Serializer
- fields: id, uploader, created_at, file, deleted, prescription
"""


class DoctorFileSerializer(_BaseFileSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='files:doctor-file-retrieve',
        lookup_field='id',
        read_only=True
    )

    download_url = serializers.HyperlinkedIdentityField(
        view_name='files:doctor-file-download',
        lookup_field='id',
        read_only=True
    )
    file = serializers.FileField(use_url=False)
    uploader = serializers.PrimaryKeyRelatedField(read_only=True)
    prescription = serializers.PrimaryKeyRelatedField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = DoctorFile
        fields = ['url', 'download_url', 'prescription', 'file', 'uploader', 'created_at']


class DoctorFlieRetrieveSerializer(DoctorFileSerializer):
    class Meta(DoctorFileSerializer.Meta):
        fields = DoctorFileSerializer.Meta.fields + ['deleted']


class DoctorFileUploadSerializer(DoctorFileSerializer):
    uploader = serializers.HiddenField(default=CurrentUserDefault())
    prescription = BasedCurrentUserPrimaryKeyRelatedField(
        queryset=Prescription.objects.select_all(), required=True)

    # doctor_upload_files = serializers.ListField(child=serializers.FileField(), write_only=True)

    class Meta(DoctorFileSerializer.Meta):
        fields = DoctorFileSerializer.Meta.fields

    def create(self, validated_data: Dict[str, Any]) -> Optional[Type[DoctorFile]]:
        uploader = validated_data.get('uploader', None)
        prescription = validated_data.get('prescription', None)

        self._validate_relation(prescription, uploader.id)
        file_object = DoctorFile.objects.create(uploader_id=uploader.id, prescription_id=prescription.id,
                                                **validated_data)
        return file_object

    def _validate_relation(self, prescription, uploader_id) -> NoReturn:
        if prescription.writer_id != uploader_id:
            raise ValidationError(detail='This user can not access this prescription!!')


class DoctorFileInPrescriptionSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='files:doctor-file-retrieve',
        lookup_field='id',
        read_only=True
    )

    download_url = serializers.HyperlinkedIdentityField(
        view_name='files:doctor-file-download',
        lookup_field='id',
        read_only=True
    )
    # prescription = serializers.PrimaryKeyRelatedField(read_only=True)
    file = serializers.FileField(use_url=False)

    class Meta:
        model = DoctorFile
        fields = ['url', 'download_url', 'file', 'created_at']


class DoctorFileDownloadSerializer(DoctorFileSerializer):
    class Meta(DoctorFileSerializer.Meta):
        fields = DoctorFileSerializer.Meta.fields


class DoctorFileListSerializer(DoctorFileSerializer):
    uploader_name = serializers.SerializerMethodField()

    class Meta(DoctorFileSerializer.Meta):
        fields = DoctorFileSerializer.Meta.fields + ['uploader_name']


class DoctorUploadedFileListSerializer(DoctorFileSerializer):
    # file = serializers.FileField(use_url=False)
    uploaded_url = serializers.HyperlinkedIdentityField(
        view_name='files:file-status-update',
        lookup_field='id',
        read_only=True
    )
    prescription = serializers.PrimaryKeyRelatedField(queryset=Prescription.objects.select_all())

    class Meta(DoctorFileSerializer.Meta):
        fields = DoctorFileSerializer.Meta.fields + ['uploaded_url']


class DoctorUploadedFileRetrieveSerializer(DoctorFileSerializer):
    prescription = BasedCurrentUserPrimaryKeyRelatedField(
        queryset=Prescription.objects.select_all(), required=False)

    class Meta(DoctorFileSerializer.Meta):
        fields = DoctorFileSerializer.Meta.fields


"""
DataFile(related Patient) Serializer
- fields: id, uploader, created_at, file, deleted, file_prescription
"""


class PatientFileSerializer(_BaseFileSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='files:patient-file-retrieve',
        lookup_field='id',
        read_only=True
    )
    download_url = serializers.HyperlinkedIdentityField(
        view_name='files:patient-file-download',
        lookup_field='id',
        read_only=True
    )
    file_prescription = CurrentPatientPrimaryKeyRelatedField(queryset=FilePrescription.objects.select_all())
    uploader = serializers.PrimaryKeyRelatedField(read_only=True)
    uploader_name = serializers.SerializerMethodField()

    class Meta:
        model = PatientFile
        fields = ['url', 'download_url', 'id', 'file_prescription', 'uploader', 'uploader_name', 'created_at']


class PatientFlieRetrieveSerializer(PatientFileSerializer):
    class Meta(PatientFileSerializer.Meta):
        fields = PatientFileSerializer.Meta.fields


class PatientFileUploadSerializer(PatientFileSerializer):
    uploader = serializers.HiddenField(default=CurrentUserDefault())
    patient_upload_files = serializers.ListField(child=serializers.FileField(), write_only=True)

    file_prescription = CurrentPatientPrimaryKeyRelatedField(
        queryset=FilePrescription.objects.select_all().filter(uploaded=False))

    class Meta(PatientFileSerializer.Meta):
        fields = PatientFileSerializer.Meta.fields + ['file', 'patient_upload_files']

    def create(self, validated_data: Dict[str, Any]) -> Optional[PatientFile]:
        uploader = validated_data.pop('uploader', None)
        file_prescription = validated_data.pop('file_prescription', None)
        files = validated_data.pop('patient_upload_files', None)

        if files is None:
            raise ValueError("'doctor_upload_files' field must be not empty")

        self._validate_relation(file_prescription, uploader)

        if uploader and file_prescription:
            file_list = []
            for file in files:
                file_list.append(PatientFile(uploader_id=uploader.id,
                                             file_prescription_id=file_prescription.id,
                                             file=file,
                                             **validated_data))

            file_objects = PatientFile.objects.bulk_create(file_list)
            # file_object = PatientFile.objects.create(uploader_id=uploader.id, file_prescription_id=file_prescription.id,
            #                                          **validated_data)
            return file_objects
        return None

    def _validate_relation(self, file_prescription, uploader):
        prescription = Prescription.objects.filter(file_prescriptions__id=file_prescription.id).first()
        if not (prescription.patient_id == uploader.id) and not (prescription.writer_id == uploader.doctor_id):
            raise ValidationError(detail='This user can not upload to file prescription!!')


class PatientFileDownloadSerializer(PatientFileSerializer):
    class Meta(PatientFileSerializer.Meta):
        fields = PatientFileSerializer.Meta.fields


class PatientFileListSerializer(PatientFileSerializer):
    uploader_name = serializers.SerializerMethodField()

    class Meta(PatientFileSerializer.Meta):
        fields = PatientFileSerializer.Meta.fields + ['uploader_name']


class PatientUploadedFileListSerializer(PatientFileSerializer):
    class Meta(PatientFileSerializer.Meta):
        fields = PatientFileSerializer.Meta.fields
