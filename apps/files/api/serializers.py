from typing import Union

from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

from files.models import DataFile, HealthStatus
from prescriptions.models import Prescription


class BasedCurrentUserPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get('request', None)
        queryset = super().get_queryset()
        if not request or not queryset:
            return None
        return queryset.filter(user=request.user.id)


"""
DataFile Serializer
"""


class RawFileSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='files:file-retrieve',
        lookup_field='id',
        read_only=True
    )

    download_url = serializers.HyperlinkedIdentityField(
        view_name='files:file-download',
        lookup_field='id',
        read_only=True
    )

    class Meta:
        model = DataFile
        fields = ['download_url', 'url', 'checked', 'status', 'created_at']


class DefaultFileSerializer(RawFileSerializer):
    class Meta(RawFileSerializer.Meta):
        # fields = ['download_url', 'url', 'checked', 'status', 'created_at', 'uploader', 'prescription']
        fields = RawFileSerializer.Meta.fields + ['uploader', 'prescription']


class FileSerializer(DefaultFileSerializer):
    uploader_name = serializers.SerializerMethodField()
    prescription_writer = serializers.SerializerMethodField()

    def get_uploader_name(self, instance):
        return getattr(instance, 'uploader_patient_name', None) or getattr(instance, 'uploader_doctor_name', None)

    def get_prescription_writer(self, instance):
        if instance.prescription is not None:
            return instance.prescription.get_writer_name()
        return None


class FileUploadSerializer(serializers.ModelSerializer):
    uploader = serializers.HiddenField(default=CurrentUserDefault())
    file = serializers.FileField(write_only=True)

    class Meta:
        model = DataFile
        fields = ['uploader', 'created_at', 'checked']

    def create(self, validated_data: dict) -> Union['DataFile', None]:
        uploader = validated_data.get('uploader', None)
        prescription = validated_data.get('prescription', None)
        prescription_id = None

        try:
            uploader_id = uploader.id
        except AttributeError('uploader is None'):
            raise

        if isinstance(prescription, Prescription):
            prescription_id = prescription.id

        file_object = DataFile.objects.create(uploader_id=uploader_id, prescription_id=prescription_id,
                                              **validated_data)
        return file_object


class FlieRetrieveSerializer(FileSerializer):
    class Meta(FileSerializer.Meta):
        # fields = ['download_url', 'url', 'checked', 'status', 'created_at', 'uploader', 'prescription']
        fields = FileSerializer.Meta.fields
        # fields = '__all__'


class FileDownloadSerializer(FileSerializer):
    class Meta(FileSerializer.Meta):
        fields = ['id'] + FileSerializer.Meta.fields


"""
DataFile(related Doctor) Serializer
"""


class DoctorFileSerializer(FileSerializer):
    uploader = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta(FileSerializer.Meta):
        # fields = ['download_url', 'url', 'checked', 'status', 'created_at', 'uploader', 'prescription']
        fields = FileSerializer.Meta.fields


class DoctorFileUploadSerializer(FileUploadSerializer):
    prescription = BasedCurrentUserPrimaryKeyRelatedField(
        queryset=Prescription.objects.select_all().defer_option_fields(), required=True)
    checked = serializers.BooleanField(read_only=True, default=True)
    status = serializers.ChoiceField(choices=HealthStatus.choices, default=HealthStatus.NORMAL)

    class Meta(FileUploadSerializer.Meta):
        # fields = ['uploader', 'created_at', 'checked', 'status', 'prescription', 'file']
        fields = FileUploadSerializer.Meta.fields + ['status', 'prescription', 'file']


class DoctorFileListSerializer(DoctorFileSerializer):
    class Meta(DoctorFileSerializer.Meta):
        # fields = ['download_url', 'url', 'checked', 'status', 'created_at',
        # 'uploader', 'uploader_name', 'prescription', 'prescription_writer']
        fields = DoctorFileSerializer.Meta.fields + ['uploader_name', 'prescription_writer']


class DoctorUploadedFileListSerializer(DoctorFileSerializer):
    # file = serializers.FileField(use_url=False)
    uploaded_url = serializers.HyperlinkedIdentityField(
        view_name='files:file-status-update',
        lookup_field='id',
        read_only=True
    )
    prescription = serializers.PrimaryKeyRelatedField(queryset=Prescription.objects.select_all())

    class Meta(DoctorFileSerializer.Meta):
        # fields = ['uploader', 'created_at', 'checked', 'uploaded_url']
        fields = DoctorFileSerializer.Meta.fields + ['uploaded_url']


class DoctorUploadedFileRetrieveSerializer(DoctorFileSerializer):
    prescription = BasedCurrentUserPrimaryKeyRelatedField(queryset=Prescription.objects.select_all(), required=False)

    class Meta(DoctorFileSerializer.Meta):
        fields = ['download_url', 'uploader', 'prescription', 'status', 'checked']


"""
DataFile(related Patient) Serializer
"""


class PatientFileSerializer(FileSerializer):
    class Meta(FileSerializer.Meta):
        fields = FileSerializer.Meta.fields


class PatientFileUploadSerializer(FileUploadSerializer):
    checked = serializers.BooleanField(read_only=True, default=False)

    class Meta(FileUploadSerializer.Meta):
        # fields = ['uploader', 'created_at', 'checked', 'file']
        fields = FileUploadSerializer.Meta.fields + ['file']


class PatientFileListSerializer(PatientFileSerializer):
    uploader_name = serializers.SerializerMethodField()
    prescription_writer = serializers.SerializerMethodField()

    class Meta(FileSerializer.Meta):
        # fields = ['download_url', 'url', 'checked', 'status', 'created_at',
        # 'uploader', 'uploader_name', 'prescription', 'prescription_writer']
        fields = FileSerializer.Meta.fields + ['uploader_name', 'prescription_writer']


class PatientUploadedFileListSerializer(PatientFileSerializer):
    class Meta(FileSerializer.Meta):
        # fields = ['uploader', 'created_at', 'checked']
        fields = FileSerializer.Meta.fields
