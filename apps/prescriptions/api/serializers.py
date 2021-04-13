from typing import Type, Optional, TYPE_CHECKING, Any, Dict, NoReturn

from django.db import transaction
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

from accounts.models import Patient
from core.api.fields import PrescriptionFields, FilePrescriptionFields
from files.api.serializers import DoctorFileInPrescriptionSerializer
from files.models import DoctorFile
from prescriptions.models import Prescription, FilePrescription

if TYPE_CHECKING:
    from django.core.files.uploadedfile import InMemoryUploadedFile


class PrescriptionModelSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='prescriptions:prescription-detail',
        lookup_field='pk',
        read_only=True
    )

    class Meta:
        model = Prescription
        fields = ['url']

    def _create_file_prescriptions(self, prescription_id, start_date, end_date):
        import datetime
        bulk_list = (
            FilePrescription(
                prescription_id=prescription_id,
                day_number=day_number + 1,
                date=start_date + datetime.timedelta(days=day_number))
            for day_number in range((end_date - start_date).days + 1))
        FilePrescription.objects.bulk_create(bulk_list)


class UpdateSupporterSerailzier(PrescriptionModelSerializer):
    @transaction.atomic
    def update(self, instance: Prescription, validated_data: Dict[str, Any]):
        self.set_delete_old_instance(instance)
        self.new_files(instance, validated_data)
        self.new_file_prescriptions(instance, validated_data)

        return super().update(instance, validated_data)

    def new_files(self, instance: Prescription, validated_data: Dict[str, Any]) -> NoReturn:
        files = validated_data.pop('update_files', None)
        if files:
            bulk_list = []
            for file in files:
                doctor_file = DoctorFile(prescription_id=instance.id, uploader_id=instance.writer_id, file=file)
                bulk_list.append(doctor_file)
            DoctorFile.objects.bulk_create(bulk_list)

    def new_file_prescriptions(self, instance: Prescription, validated_data: Dict[str, Any]):
        start_date = validated_data.pop('start_date', None)
        end_date = validated_data.pop('end_date', None)
        if start_date and end_date:
            self._create_file_prescriptions(instance.id, start_date, end_date)

    def set_delete_old_instance(self, instance: Prescription) -> NoReturn:
        instance.doctor_files.update(deleted=True)
        instance.file_prescriptions.update(deleted=True)


class CreateSupporterSerializer(PrescriptionModelSerializer):
    @transaction.atomic
    def create(self, validated_data: Dict[str, Any]):
        field_name = 'doctor_upload_files'
        files = validated_data.pop(field_name, None)
        start_date = validated_data.pop('start_date', None)
        end_date = validated_data.pop('end_date', None)
        prescription = self._create_prescription(validated_data)
        self._create_file_prescriptions(prescription_id=prescription.id,
                                        start_date=start_date,
                                        end_date=end_date)
        if files:
            self._create_doctor_files(writer_id=prescription.writer_id,
                                      prescription_id=prescription.id,
                                      request_files=files)
        return prescription

    def _create_prescription(self, validated_data: Dict[str, Any]) -> 'Prescription':
        user = validated_data.pop('writer')
        writer = user.doctor
        return Prescription.objects.create(writer=writer, **validated_data)

    def _create_doctor_files(self,
                             writer_id: int,
                             prescription_id: int,
                             request_files: 'InMemoryUploadedFile') -> NoReturn:
        uploader_id = writer_id
        file_list = []
        for file in request_files:
            file_list.append(DoctorFile(uploader_id=uploader_id, prescription_id=prescription_id, file=file))
        DoctorFile.objects.bulk_create(file_list)


class FilePrescriptionModelSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='prescriptions:file-prescription-detail',
        lookup_field='pk',
        read_only=True
    )

    class Meta:
        model = FilePrescription
        fields = ['url']


class FilteredPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def __init__(self, target_field: str = None, **kwargs):
        super().__init__(**kwargs)
        self.target_field = target_field

    def get_queryset(self) -> Optional[Type['QuerySet']]:
        request = self.context.get('request', None)
        if not request:
            return None

        query = {self.target_field: request.user.id}
        return super().get_queryset().filter(**query)


class PrescriptionListSerializer(PrescriptionModelSerializer):
    status = serializers.CharField(source='get_status_display')

    class Meta:
        model = Prescription
        fields = ['url'] + PrescriptionFields.list_field


class PrescriptionDetailSerializer(PrescriptionListSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='prescriptions:prescription-update',
        lookup_field='pk',
    )

    class Meta:
        model = Prescription
        fields = ['url'] + PrescriptionFields.detail_field


class PrescriptionUpdateSerializer(UpdateSupporterSerailzier):
    writer = serializers.HiddenField(default=CurrentUserDefault())
    doctor_files = serializers.SerializerMethodField()
    update_files = serializers.ListField(child=serializers.FileField(), write_only=True)

    class Meta:
        model = Prescription
        fields = ['url', 'writer', 'status', 'description', 'update_files', 'doctor_files',
                  'start_date', 'end_date', 'checked']

    def get_doctor_files(self, instance):
        doctor_files = DoctorFile.objects.filter(prescription_id=instance.id).filter_not_deleted()
        serializer = DoctorFileInPrescriptionSerializer(instance=doctor_files, many=True, read_only=True,
                                                        context=self.context)
        return serializer.data


class PrescriptionCreateSerializer(CreateSupporterSerializer):
    writer = serializers.HiddenField(default=CurrentUserDefault())
    patient = FilteredPrimaryKeyRelatedField(queryset=Patient.objects.select_all(),
                                             write_only=True, target_field='doctor_id')
    doctor_files = DoctorFileInPrescriptionSerializer(many=True, read_only=True)
    doctor_upload_files = serializers.ListField(child=serializers.FileField(), write_only=True)
    checked = serializers.BooleanField(default=False, read_only=True)

    class Meta(PrescriptionDetailSerializer.Meta):
        fields = ['url'] + PrescriptionFields.detail_field + ['doctor_files', 'doctor_upload_files']


class PrescriptionChoiceSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_display')
    writer_name = serializers.SerializerMethodField()
    patient_name = serializers.SerializerMethodField()

    class Meta:
        model = Prescription
        fields = ['id', 'writer_id', 'patient_id', 'writer_name', 'patient_name', 'start_date', 'end_date',
                  'created_at', 'status', 'checked']

    def get_patient_name(self, instance):
        return instance.patient_name

    def get_writer_name(self, instance):
        return instance.writer_name


class FilePrescriptionListSerializer(FilePrescriptionModelSerializer):
    uploaded = serializers.BooleanField(read_only=True)
    status = serializers.CharField(source='get_status_display')

    class Meta(FilePrescriptionModelSerializer.Meta):
        fields = FilePrescriptionFields.list_field


class FilePrescriptionDetailSerializer(FilePrescriptionListSerializer):
    class Meta(FilePrescriptionListSerializer.Meta):
        fields = ['url'] + FilePrescriptionFields.detail_field


class FilePrescriptionUpdateSerializer(FilePrescriptionModelSerializer):
    class Meta(FilePrescriptionModelSerializer.Meta):
        fields = ['url', 'status', 'active', 'checked', 'description']


class FilePrescriptionCreateSerializer(FilePrescriptionModelSerializer):
    prescription = serializers.PrimaryKeyRelatedField(queryset=Prescription.objects.select_all())

    class Meta:
        model = FilePrescription
        fields = ['url', 'prescription', 'description', 'status', 'date', 'day_number', 'checked']


class FilePrescriptionChoiceSerializer(serializers.ModelSerializer):
    writer_id = serializers.SerializerMethodField()
    writer_name = serializers.SerializerMethodField()
    patient_id = serializers.SerializerMethodField()
    patient_name = serializers.SerializerMethodField()

    class Meta:
        model = FilePrescription
        fields = ['id', 'prescription_id', 'writer_id', 'writer_name', 'patient_id', 'patient_name', 'status',
                  'checked', 'created_at', 'day_number', 'date', 'uploaded']

    def get_writer_id(self, instance):
        return instance.writer_id

    def get_writer_name(self, instance):
        return instance.writer_name

    def get_patient_id(self, instance):
        return instance.patient_id

    def get_patient_name(self, instance):
        return instance.patient_name
