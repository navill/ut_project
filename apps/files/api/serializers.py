from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

from accounts.models import BaseUser, Patient
from files.models import DataFile
from prescriptions.models import Prescription


class DefaultFileSerializer(serializers.ModelSerializer):
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
        fields = ['download_url', 'url', 'uploader', 'patient', 'created_at']


class FlieListSerializer(DefaultFileSerializer):
    # uploader = serializers.SerializerMethodField()
    uploader = serializers.PrimaryKeyRelatedField(queryset=BaseUser.objects.all())
    # patient = serializers.SerializerMethodField()
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())

    class Meta(DefaultFileSerializer.Meta):
        fields = DefaultFileSerializer.Meta.fields

    def get_uploader(self, instance):
        user = instance.uploader.get_child_account()
        return user.get_full_name()

    def get_patient(self, instance):
        return instance.patient.get_full_name()


class FlieRetrieveSerializer(DefaultFileSerializer):
    class Meta(DefaultFileSerializer.Meta):
        fields = DefaultFileSerializer.Meta.fields


class FileUploadSerializer(serializers.ModelSerializer):
    hidden_uploader = serializers.HiddenField(default=CurrentUserDefault())
    uploader = serializers.PrimaryKeyRelatedField(queryset=BaseUser.objects.all())
    # patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    prescription = serializers.PrimaryKeyRelatedField(queryset=Prescription.objects.all())
    file = serializers.FileField(use_url=False)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = DataFile
        fields = ['hidden_uploader', 'uploader', 'prescription', 'file', 'created_at']
        read_only_fields = ['hidden_uploader']
        write_only_fields = ['file']

    def create(self, validated_data: dict) -> DataFile:
        try:
            uploader = validated_data.pop('hidden_uploader')
            # using celery
            file_object = DataFile.objects.create(uploader_id=uploader.id, **validated_data)
        except Exception:
            raise
        return file_object
