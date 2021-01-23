from typing import Type, Optional, Dict, Any

from django.db import transaction
from django.db.models import QuerySet
from django.utils.datastructures import MultiValueDict
from rest_framework import serializers

from accounts.models import Patient
from files.api.serializers import PatientUploadedFileListSerializer, DoctorFileInPrescriptionSerializer
from files.models import DoctorFile
from prescriptions.models import Prescription, HealthStatus, FilePrescription


class CurrentDoctorDefault:
    requires_context = True

    def __call__(self, serializer_field):
        return serializer_field.context['request'].user.doctor

    def __repr__(self):
        return '%s()' % self.__class__.__name__


class FilteredPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def __init__(self, related_id: str = None, **kwargs):
        super().__init__(**kwargs)
        self.related_id = related_id

    def get_queryset(self) -> Optional[Type[QuerySet]]:
        request = self.context.get('request', None)
        if not request:
            return None

        query = {self.related_id: request.user.id}
        return super().get_queryset().filter(**query)


class DefaultPrescriptionSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='prescriptions:detail-update',
        lookup_field='pk'
    )
    writer = serializers.PrimaryKeyRelatedField(read_only=True)
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.select_all())
    description = serializers.CharField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Prescription
        fields = ['url', 'id', 'writer', 'patient', 'description', 'created_at', 'updated_at']


class PrescriptionSerializer(DefaultPrescriptionSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='prescriptions:prescription-detail-update',
        lookup_field='pk'
    )
    writer = serializers.HiddenField(default=CurrentDoctorDefault())
    patient = FilteredPrimaryKeyRelatedField(queryset=Patient.objects.select_all(),
                                             write_only=True, related_id='doctor_id')
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    checked = serializers.BooleanField(default=False)

    writer_name = serializers.SerializerMethodField(read_only=True)
    patient_name = serializers.SerializerMethodField(read_only=True)

    class Meta(DefaultPrescriptionSerializer.Meta):
        fields = DefaultPrescriptionSerializer.Meta.fields + ['writer_name', 'patient_name', 'doctor_files',
                                                              'start_date', 'end_date', 'status', 'checked', 'url']

    def get_writer_name(self, instance: Prescription) -> str:
        if hasattr(instance, 'writer_name'):
            return instance.writer_name
        # queryset에 writer_name이 없을 경우
        return instance.writer.get_full_name()

    def get_patient_name(self, instance: Prescription) -> str:
        if hasattr(instance, 'patient_name'):
            return instance.patient_name
        return instance.patient.get_full_name()

    # def create(self, validated_data: Dict[str, Any]) -> Prescription:
    #     validated_data['writer'] = validated_data['writer'].doctor
    #     files = validated_data.pop('files')
    #     prescription_obj = super().create(validated_data)
    #     MyModel.objects.filter(pk=obj.pk).update(val=F('val') + 1)
    #     for file in files:
    #         photo = Prescription.objects.create(image=img, blogs=blogs, **validated_data)
    #     return photo
    #     return
    # def create(self, validated_data: Dict[str, Any]) -> Optional[Type[DoctorFile]]:
    #     writer = validated_data.get('writer').doctor
    #     uploader = writer
    #     prescription = validated_data.get('prescription', None)
    #     files = validated_data.pop('files', None)
    #     file_object = None
    #
    #     uploader_id, prescription_id = (uploader.id, prescription.id) \
    #         if isinstance(uploader, User) and isinstance(prescription, Prescription) \
    #         else (uploader, prescription)
    #     for file in files:
    #         file_object = DoctorFile.objects.create(uploader_id=uploader_id, prescription_id=prescription_id,
    #                                                 file=file, **validated_data)
    #     return file_object


class TempDictField(serializers.DictField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_representation(self, value):
        for key, value in value.items():
            print(key, value)
        dict_value = {
            str(key): self.child.to_representation(val) if val is not None else None
            for key, val in value.items()
        }

        return dict_value


class PrescriptionCreateSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='prescriptions:prescription-detail-update',
        lookup_field='pk'
    )
    writer = serializers.HiddenField(default=CurrentDoctorDefault())
    patient = FilteredPrimaryKeyRelatedField(queryset=Patient.objects.select_all(),
                                             write_only=True, related_id='doctor_id')
    # doctor_files = serializers.DictField(child=DoctorFileInPrescriptionSerializer(many=True))
    doctor_files = DoctorFileInPrescriptionSerializer(many=True, read_only=True)
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    checked = serializers.BooleanField(default=False)

    class Meta(DefaultPrescriptionSerializer.Meta):
        fields = DefaultPrescriptionSerializer.Meta.fields + ['doctor_files', 'start_date', 'end_date', 'status',
                                                              'checked', 'url']

    @transaction.atomic
    def create(self, validated_data: Dict[str, Any]):
        writer = validated_data.pop('writer')
        request_files = self.context['request'].FILES
        files = self._validate_file_fieldname(request_files)

        prescription = Prescription.objects.create(writer=writer, **validated_data)
        for file in files:
            DoctorFile.objects.create(uploader_id=writer.user_id, prescription_id=prescription.id, file=file)
        return prescription

    def _validate_file_fieldname(self, file_keys: MultiValueDict):
        for key in file_keys.keys():
            if 'upload_file' not in key:
                raise ValueError("file field name is not 'upload_file'")
        return file_keys


class FilePrescriptionSerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedIdentityField(
    #     view_name='prescriptions:file-prescription-detail-update',
    #     lookup_field='pk'
    # )
    # id = serializers.IntegerField(read_only=True)
    description = serializers.CharField(default='')
    status = serializers.ChoiceField(choices=HealthStatus.choices)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(read_only=True)
    prescription = serializers.PrimaryKeyRelatedField(read_only=True)
    day_number = serializers.IntegerField(read_only=True)
    active = serializers.BooleanField()
    uploaded = serializers.BooleanField()
    checked = serializers.BooleanField()

    class Meta:
        model = FilePrescription
        fields = ['id', 'prescription', 'description', 'status', 'day_number', 'deleted', 'active',
                  'uploaded', 'checked', 'created_at', 'updated_at']  # + ['url']


class FilePrescriptionListSerializer(FilePrescriptionSerializer):
    pass


class FilePrescriptionCreateSerializer(FilePrescriptionSerializer):
    prescription = serializers.PrimaryKeyRelatedField(queryset=Prescription.objects.select_all())

    class Meta(FilePrescriptionSerializer.Meta):
        fields = FilePrescriptionSerializer.Meta.fields


class FilePrescriptionRetrieveUpdateSerializer(FilePrescriptionSerializer):
    class Meta(FilePrescriptionSerializer.Meta):
        fields = FilePrescriptionSerializer.Meta.fields


class NestedFilePrescriptionSerializer(FilePrescriptionSerializer):
    patient_files = PatientUploadedFileListSerializer(many=True)  # + PatientSerializer

    class Meta(FilePrescriptionSerializer.Meta):
        fields = FilePrescriptionSerializer.Meta.fields + ['patient_files']


class NestedPrescriptionSerializer(PrescriptionSerializer):
    file_prescriptions = NestedFilePrescriptionSerializer(many=True)

    class Meta(PrescriptionSerializer.Meta):
        fields = PrescriptionSerializer.Meta.fields + ['file_prescriptions']
