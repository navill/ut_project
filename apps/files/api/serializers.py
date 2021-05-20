from typing import Optional, Type, Union, TYPE_CHECKING

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

from files.temp_models import TempHospitalFiles
from files.models import DoctorFile, PatientFile

from prescriptions.models import Prescription, FilePrescription, PrescriptionQuerySet, FilePrescriptionQuerySet

if TYPE_CHECKING:
    from django.db.models import QuerySet

User = get_user_model()


class CurrentUserPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self) -> Union[PrescriptionQuerySet, FilePrescriptionQuerySet]:
        request = self.context.get('request', None)
        user_id = request.user.id
        queryset = super().get_queryset()

        if isinstance(queryset, PrescriptionQuerySet):
            query_param = {'user': user_id}
        elif isinstance(queryset, FilePrescriptionQuerySet):
            query_param = {'patient_id': user_id}
        else:
            raise Exception('invalid queryset')

        return queryset.filter(**query_param)


class CurrentPatientPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self) -> Optional[Type['QuerySet']]:
        request = self.context.get('request', None)
        queryset = super().get_queryset()
        return queryset.filter(prescription__patient_id=request.user.id)


class _BaseFileSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(default=False)

    def get_uploader_name(self, instance: User):
        return getattr(instance, 'uploader_patient_name', None) or getattr(instance, 'uploader_doctor_name', None)


class DoctorFileSerializer(_BaseFileSerializer):
    download_url = serializers.HyperlinkedIdentityField(
        view_name='files:doctor-file-download',
        lookup_field='id',
        read_only=True,
    )
    file = serializers.FileField(use_url=False)
    uploader = serializers.PrimaryKeyRelatedField(read_only=True)
    prescription = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = DoctorFile
        fields = ['id', 'download_url', 'prescription', 'file', 'uploader', 'created_at']


class DoctorFileListSerializer(DoctorFileSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='files:doctor-file-retrieve',
        lookup_field='id',
    )
    uploader_name = serializers.SerializerMethodField(read_only=True)

    class Meta(DoctorFileSerializer.Meta):
        fields = ['url'] + DoctorFileSerializer.Meta.fields + ['uploader_name']


class DoctorFlieRetrieveSerializer(DoctorFileSerializer):
    update_url = serializers.HyperlinkedIdentityField(
        view_name='files:doctor-file-update',
        lookup_field='id',
        read_only=True
    )

    class Meta(DoctorFileSerializer.Meta):
        fields = ['update_url', 'deleted'] + DoctorFileSerializer.Meta.fields


class DoctorFileUpdateSerializer(serializers.ModelSerializer):
    file = serializers.FileField(use_url=False)
    deleted = serializers.BooleanField()

    class Meta:
        model = DoctorFile
        fields = ['file', 'deleted']


class DoctorFileUploadSerializer(DoctorFileSerializer):
    uploader = serializers.HiddenField(default=CurrentUserDefault())
    prescription = CurrentUserPrimaryKeyRelatedField(queryset=Prescription.objects.select_all(),
                                                     required=True)
    file = serializers.FileField(write_only=True)

    class Meta(DoctorFileSerializer.Meta):
        fields = DoctorFileSerializer.Meta.fields


class DoctorFileInPrescriptionSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='files:doctor-file-retrieve',
                                               lookup_field='id',
                                               read_only=True,
                                               )
    download_url = serializers.HyperlinkedIdentityField(view_name='files:doctor-file-download',
                                                        lookup_field='id',
                                                        read_only=True,
                                                        )
    file = serializers.FileField(use_url=False)

    class Meta:
        model = DoctorFile
        fields = ['url', 'id', 'download_url', 'file', 'created_at', 'updated_at', 'deleted']


class DoctorFileDownloadSerializer(DoctorFileSerializer):
    class Meta(DoctorFileSerializer.Meta):
        fields = DoctorFileSerializer.Meta.fields


class DoctorUploadedFileListSerializer(DoctorFileSerializer):
    uploaded_url = serializers.HyperlinkedIdentityField(
        view_name='files:file-status-update',
        lookup_field='id',
        read_only=True
    )
    prescription = serializers.PrimaryKeyRelatedField(queryset=Prescription.objects.select_all())

    class Meta(DoctorFileSerializer.Meta):
        fields = DoctorFileSerializer.Meta.fields + ['uploaded_url']


class DoctorUploadedFileRetrieveSerializer(DoctorFileSerializer):
    prescription = CurrentUserPrimaryKeyRelatedField(
        queryset=Prescription.objects.select_all(), required=False)

    class Meta(DoctorFileSerializer.Meta):
        fields = DoctorFileSerializer.Meta.fields


"""
DataFile(Patient) Serializer
- fields: id, uploader, created_at, file, deleted, file_prescription
"""


class PatientFileSerializer(_BaseFileSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='files:patient-file-retrieve',
        lookup_field='id',
        read_only=True,
    )
    download_url = serializers.HyperlinkedIdentityField(
        view_name='files:patient-file-download',
        lookup_field='id',
        read_only=True,
    )
    file_prescription = CurrentPatientPrimaryKeyRelatedField(queryset=FilePrescription.objects.select_all(),
                                                             write_only=True)
    uploader = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = PatientFile
        fields = ['url', 'download_url', 'id', 'file_prescription', 'file', 'uploader', 'created_at']


class PatientFlieRetrieveSerializer(PatientFileSerializer):
    update_url = serializers.HyperlinkedIdentityField(
        view_name='files:patient-file-update',
        lookup_field='id',
        read_only=True,
    )
    uploader_name = serializers.SerializerMethodField()
    file = serializers.FileField()

    class Meta(PatientFileSerializer.Meta):
        fields = ['update_url'] + PatientFileSerializer.Meta.fields + ['file', 'uploader_name']


class PatientFlieUpdateSerializer(PatientFileSerializer):
    class Meta(PatientFileSerializer.Meta):
        fields = PatientFileSerializer.Meta.fields


class PatientFileUploadSerializer(PatientFileSerializer):
    uploader = serializers.HiddenField(default=CurrentUserDefault())
    file_prescription = CurrentUserPrimaryKeyRelatedField(queryset=FilePrescription.objects.select_all(), required=True)
    file = serializers.FileField(use_url=False)

    class Meta(PatientFileSerializer.Meta):
        fields = PatientFileSerializer.Meta.fields + ['file']


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


class TempFileSerializer(serializers.ModelSerializer):
    file = serializers.FileField(use_url=False, write_only=True)
    file_type = serializers.CharField(read_only=True)
    file_name = serializers.CharField(read_only=True)
    extension = serializers.CharField(read_only=True)

    class Meta:
        model = TempHospitalFiles
        fields = '__all__'
