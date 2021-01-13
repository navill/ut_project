from typing import Union

from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

from files.models import DataFile, HealthStatus
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
        fields = ['download_url', 'url', 'uploader', 'prescription', 'created_at']


class DoctorFileListSerializer(DefaultFileSerializer):
    uploader_name = serializers.SerializerMethodField()

    class Meta(DefaultFileSerializer.Meta):
        fields = DefaultFileSerializer.Meta.fields + ['uploader_name']

    def get_uploader_name(self, instance):
        return instance.uploader.get_child_username()


class PatientFileListSerializer(DefaultFileSerializer):
    uploader = serializers.SerializerMethodField()

    class Meta(DefaultFileSerializer.Meta):
        fields = DefaultFileSerializer.Meta.fields + ['checked']

    def get_uploader(self, instance):
        return instance.uploader.get_child_username()


class FlieRetrieveSerializer(DefaultFileSerializer):
    class Meta(DefaultFileSerializer.Meta):
        fields = DefaultFileSerializer.Meta.fields


class FileDownloadSerializer(DefaultFileSerializer):
    class Meta(DefaultFileSerializer.Meta):
        fields = ['id'] + DefaultFileSerializer.Meta.fields


"""
FileUpload 순서
[Doctor] -> Core Serializer에서 처리
PrescriptionSerializer + FileUploadSerializer
Prescription 작성 -> File 첨부 -> Prescription 객체 생성 -> File 객체 생성(prescription 필드에 앞서 생성된 Prescription 객체 추가)

[Patient] -> Core Serializer에서 처리
File 첨부 -> File 객체 생성
"""


class DefaultFileUploadSerializer(serializers.ModelSerializer):
    """
    patient 또는 doctor가 파일 업로드에 사용
    - 의사가 파일을 업로드할 경우 prescription과 관계를 형성해야한다.
    - 환자가 파일을 업로드할 경우 prescription과 관계를 형성하지 않는다.
    - 의사가 prescription detail 페이지에서 환자가 업로드한 파일을 체크(checked=True)할 경우, 해당 파일은 prescription과 관계를 형성한다.
    """
    hidden_uploader = serializers.HiddenField(default=CurrentUserDefault())
    file = serializers.FileField(use_url=False)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = DataFile
        fields = ['hidden_uploader', 'file', 'created_at']
        read_only_fields = ['hidden_uploader', 'created_at']

    def create(self, validated_data: dict) -> Union['DataFile', None]:
        uploader = validated_data.get('hidden_uploader', None)
        prescription = validated_data.get('prescription', None)

        if uploader is None:
            # raise ValueError('uploader should be not None')
            return None
        if prescription is not None:
            prescription = prescription.id

        file_object = DataFile.objects.create(uploader_id=uploader.id, prescription_id=prescription,
                                              file=validated_data['file'])
        return file_object


class WriterFilteredPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get('request', None)
        queryset = super().get_queryset()
        if not request or not queryset:
            return None
        return queryset.filter(writer_id=request.user.id)


class DoctorFileUploadSerializer(DefaultFileUploadSerializer):
    prescription = WriterFilteredPrimaryKeyRelatedField(queryset=Prescription.objects.all(), required=False)
    checked = serializers.BooleanField(default=True)
    status = serializers.ChoiceField(choices=HealthStatus.choices, default=HealthStatus.NORMAL)

    class Meta(DefaultFileUploadSerializer.Meta):
        fields = DefaultFileUploadSerializer.Meta.fields + ['prescription', 'checked', 'status']


class PatientFileUploadSerializer(DefaultFileUploadSerializer):
    class Meta(DefaultFileUploadSerializer.Meta):
        fields = DefaultFileUploadSerializer.Meta.fields


class DoctorUploadedFileListSerializer(DefaultFileSerializer):
    """
    doctor-main page에서 환자가 새로 업로드한 파일 리스트 출력
    의사가 checked를 True로 변경할 경우 리스트에서 해당 값은 사라진다.
    """
    file = serializers.FileField(use_url=False)
    uploaded_url = serializers.HyperlinkedIdentityField(
        view_name='files:file-status-update',
        lookup_field='id',
        read_only=True
    )

    class Meta:
        model = DataFile
        fields = ['download_url', 'url', 'uploaded_url', 'uploader', 'file', 'checked', 'created_at']


class PatientUploadedFileListSerializer(DefaultFileSerializer):
    """
    doctor-main page에서 환자가 새로 업로드한 파일 리스트 출력
    의사가 checked를 True로 변경할 경우 리스트에서 해당 값은 사라진다.
    """
    file = serializers.FileField(use_url=False)

    class Meta(DefaultFileSerializer.Meta):
        fields = ['download_url', 'uploader', 'file', 'checked', 'created_at']


class UploadedFileUpdateSerializer(DefaultFileSerializer):
    uploaded_url = serializers.HyperlinkedIdentityField(
        view_name='files:file-status-update',
        lookup_field='id',
        read_only=True
    )
    prescription = WriterFilteredPrimaryKeyRelatedField(queryset=Prescription.objects.all(), required=False)

    class Meta:
        model = DataFile
        fields = ['download_url', 'uploaded_url', 'prescription', 'status', 'checked', 'created_at']
