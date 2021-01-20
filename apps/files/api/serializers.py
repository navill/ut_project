from typing import Union

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

from files.models import DoctorFile, PatientFile
from prescriptions.models import Prescription, HealthStatus, FilePrescription

User = get_user_model()


class BasedCurrentUserPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get('request', None)
        queryset = super().get_queryset()
        if not request or not queryset:
            return None
        return queryset.filter(user=request.user.id)


"""
BaseFile Serializer
- fields: url, download_url, created_at, file, deleted
"""


class _BaseFileSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(default=False, read_only=True)

    def get_uploader_name(self, instance):
        return getattr(instance, 'uploader_patient_name', None) or getattr(instance, 'uploader_doctor_name', None)


# class DefaultFileSerializer(RawFileSerializer):
#     class Meta(RawFileSerializer.Meta):
#         # fields = ['download_url', 'url', 'checked', 'status', 'created_at', 'uploader', 'prescription']
#         fields = RawFileSerializer.Meta.fields + ['uploader', 'prescription']


# class _FileSerializer(_BaseFileSerializer):

# prescription_writer = serializers.SerializerMethodField()

# def get_uploader_name(self, instance):
#     return getattr(instance, 'uploader_patient_name', None) or getattr(instance, 'uploader_doctor_name', None)

# def get_prescription_writer(self, instance):
#     if instance.prescription is not None:
#         return instance.prescription.get_writer_name()
#     return None


#
# class FileUploadSerializer(serializers.ModelSerializer):
#     uploader = serializers.HiddenField(default=CurrentUserDefault())
#     file = serializers.FileField(write_only=True)
#
#     class Meta:
#         model = DataFile
#         fields = ['uploader', 'created_at', 'checked']
#
#     def create(self, validated_data: dict) -> Union['DataFile', None]:
#         uploader = validated_data.get('uploader', None)
#         prescription = validated_data.get('prescription', None)
#         prescription_id = None
#
#         try:
#             uploader_id = uploader.id
#         except AttributeError('uploader is None'):
#             raise
#
#         if isinstance(prescription, Prescription):
#             prescription_id = prescription.id
#
#         file_object = DataFile.objects.create(uploader_id=uploader_id, prescription_id=prescription_id,
#                                               **validated_data)
#         return file_object
#
#
# class FlieRetrieveSerializer(FileSerializer):
#     class Meta(FileSerializer.Meta):
#         # fields = ['download_url', 'url', 'checked', 'status', 'created_at', 'uploader', 'prescription']
#         fields = FileSerializer.Meta.fields
#         # fields = '__all__'
#
#
# class FileDownloadSerializer(FileSerializer):
#     class Meta(FileSerializer.Meta):
#         fields = ['id'] + FileSerializer.Meta.fields


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
        fields = ['id', 'url', 'download_url', 'prescription', 'file', 'uploader', 'created_at']


class DoctorFlieRetrieveSerializer(DoctorFileSerializer):
    class Meta(DoctorFileSerializer.Meta):
        fields = DoctorFileSerializer.Meta.fields + ['deleted']


class DoctorFileUploadSerializer(DoctorFileSerializer):
    uploader = serializers.HiddenField(default=CurrentUserDefault())
    prescription = BasedCurrentUserPrimaryKeyRelatedField(
        queryset=Prescription.objects.select_all(), required=True)

    class Meta(DoctorFileSerializer.Meta):
        fields = DoctorFileSerializer.Meta.fields

    def create(self, validated_data: dict):
        uploader = validated_data.get('uploader', None)
        prescription = validated_data.get('prescription', None)
        # try:
        #     uploader_id = uploader.id
        # except AttributeError('uploader is None'):
        #     raise
        uploader_id, prescription_id = (uploader.id, prescription.id) \
            if isinstance(uploader, User) and isinstance(prescription, Prescription) \
            else (uploader, prescription)
        file_object = DoctorFile.objects.create(uploader_id=uploader_id, prescription_id=prescription_id,
                                                **validated_data)
        return file_object


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
    file_prescription = serializers.PrimaryKeyRelatedField(queryset=FilePrescription.objects.all())

    class Meta:
        model = PatientFile.objects.select_all()
        fields = ['url', 'download_url', 'file_prescription', 'uploader', 'uploader_name', 'created_at']


class PatientFlieRetrieveSerializer(PatientFileSerializer):
    class Meta(PatientFileSerializer.Meta):
        fields = PatientFileSerializer.Meta.fields


class PatientFileUploadSerializer(PatientFileSerializer):
    uploader = serializers.HiddenField(default=CurrentUserDefault())
    checked = serializers.BooleanField(read_only=True, default=False)

    class Meta(PatientFileSerializer.Meta):
        # fields = ['uploader', 'created_at', 'checked', 'file']
        fields = PatientFileSerializer.Meta.fields + ['file']

    def create(self, validated_data: dict) -> Union['DataFile', None]:
        uploader = validated_data.get('uploader', None)
        prescription_id = validated_data.get('file_prescription', None)

        try:
            uploader_id = uploader.id
        except AttributeError('uploader is None'):
            raise

        file_object = PatientFile.objects.create(uploader_id=uploader_id, file_prescription_id=prescription_id,
                                                 **validated_data)
        return file_object


class PatientFileDownloadSerializer(PatientFileSerializer):
    class Meta(PatientFileSerializer.Meta):
        fields = PatientFileSerializer.Meta.fields


class PatientFileListSerializer(PatientFileSerializer):
    uploader_name = serializers.SerializerMethodField()
    prescription_writer = serializers.SerializerMethodField()

    class Meta(PatientFileSerializer.Meta):
        # fields = ['download_url', 'url', 'checked', 'status', 'created_at',
        # 'uploader', 'uploader_name', 'prescription', 'prescription_writer']
        fields = PatientFileSerializer.Meta.fields + ['uploader_name', 'prescription_writer']


class PatientUploadedFileListSerializer(PatientFileSerializer):
    class Meta(PatientFileSerializer.Meta):
        # fields = ['uploader', 'created_at', 'checked']
        fields = PatientFileSerializer.Meta.fields
