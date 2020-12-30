from typing import *

from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from rest_framework.reverse import reverse

from accounts.models import Patient, Doctor, BaseUser
from files.models import DataFile


class DefaultFileSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()
    doctor = serializers.SerializerMethodField()
    patient = serializers.SerializerMethodField()

    class Meta:
        model = DataFile
        fields = ['download_url', 'url', 'uploader', 'doctor', 'patient', 'created_at']

    def get_download_url(self, instance):
        url = reverse('files:file-download', kwargs={'id': instance.id}, request=self.context['request'])
        return url

    def get_url(self, instance):
        url = reverse('files:file-retrieve', kwargs={'id': instance.id}, request=self.context['request'])
        return url

    def get_doctor(self, instance):
        return str(instance.doctor.full_name)

    def get_patient(self, instance):
        return str(instance.patient.full_name)


class FlieListSerializer(DefaultFileSerializer):
    class Meta(DefaultFileSerializer.Meta):
        fields = DefaultFileSerializer.Meta.fields


class FlieRetrieveSerializer(DefaultFileSerializer):
    class Meta(DefaultFileSerializer.Meta):
        fields = DefaultFileSerializer.Meta.fields


class FileUploadSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    hidden_uploader = serializers.HiddenField(default=CurrentUserDefault())
    uploader = serializers.PrimaryKeyRelatedField(queryset=BaseUser.objects.all())
    # doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    file = serializers.FileField(use_url=False)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = DataFile
        fields = ['url', 'hidden_uploader', 'uploader', 'patient', 'file', 'created_at']
        read_only_fields = ['id', 'uploader']
        write_only_fields = ['file']

    def create(self, validated_data: dict) -> DataFile:
        try:
            uploader = validated_data.pop('hidden_uploader')
            file_obj = DataFile.objects.create(uploader_id=uploader.id, **validated_data)
        except Exception:
            raise
        return file_obj

    def get_url(self, instance):
        url = reverse('files:file-download', kwargs={'uuid': instance.id}, request=self.context['request'])
        return url
