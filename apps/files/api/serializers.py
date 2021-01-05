from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

from accounts.models import BaseUser
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
        fields = ['download_url', 'url', 'uploader', 'created_at']


class FlieListSerializer(DefaultFileSerializer):
    # uploader = serializers.PrimaryKeyRelatedField(queryset=BaseUser.objects.all())
    uploader = serializers.SerializerMethodField()

    class Meta(DefaultFileSerializer.Meta):
        fields = DefaultFileSerializer.Meta.fields

    def get_uploader(self, instance):
        if instance.uploader is None:
            pass
        else:
            user = instance.uploader.doctor
            return user.get_full_name()

    # def get_patient(self, instance):
    #     return instance.patient.get_full_name()


class FlieRetrieveSerializer(DefaultFileSerializer):
    class Meta(DefaultFileSerializer.Meta):
        fields = DefaultFileSerializer.Meta.fields


"""
FileUpload 순서
[Doctor] -> Core Serializer에서 처리
PrescriptionSerializer + FileUploadSerializer
Prescription 작성 -> File 첨부 -> Prescription 객체 생성 -> File 객체 생성(prescription 필드에 앞서 생성된 Prescription 객체 추가)

[Patient] -> Core Serializer에서 처리
File 첨부 -> File 객체 생성

"""


class FileUploadSerializer(serializers.ModelSerializer):
    """
    patient 또는 doctor가 파일 업로드에 사용
    - 의사가 파일을 업로드할 경우 prescription과 관계를 형성해야한다.
    - 환자가 파일을 업로드할 경우 prescription과 관계를 형성하지 않는다.
    - 의사가 prescription detail 페이지에서 환자가 업로드한 파일을 체크(checked=True)할 경우, 해당 파일은 prescription과 관계를 형성한다.
    """
    hidden_uploader = serializers.HiddenField(default=CurrentUserDefault())
    uploader = serializers.PrimaryKeyRelatedField(queryset=BaseUser.objects.all())
    # patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    prescription = serializers.PrimaryKeyRelatedField(queryset=Prescription.objects.all(), required=False)
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


class UploadedFileListSerializer(DefaultFileSerializer):
    """
    doctor-main page에서 환자가 새로 업로드한 파일 리스트 출력
    의사가 checked를 True로 변경할 경우 리스트에서 해당 값은 사라진다.
    """
    file = serializers.FileField(use_url=False)

    class Meta:
        model = DataFile
        fields = ['download_url', 'url', 'uploader', 'checked', 'status', 'file', 'created_at']
