from abc import ABCMeta, abstractmethod
from typing import Type, Optional, TYPE_CHECKING, Any, Dict, NoReturn

from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
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


class NewAbstract(metaclass=ABCMeta):
    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def validate_status(self):
        pass


class NewFiles(NewAbstract):
    """
    CREATE OR UPDATE
    """

    def __init__(self, invoker):
        self.upload_files = invoker.upload_files
        self.instance = invoker.prescription
        self.is_update = invoker.is_update
        self.status = False
        self.validate_status()

    def validate_status(self):
        if self.upload_files:
            self.status = True
        else:
            self.status = False

    def execute(self):
        if self.is_update:
            self.delete_old_instance_for_update()
        self.create_doctor_files(self.upload_files, self.instance)

    def delete_old_instance_for_update(self):
        self.instance.doctor_files.update(deleted=True)

    def create_doctor_files(self, upload_files, instance):
        bulk_list = []
        for file in upload_files:
            doctor_file = DoctorFile(prescription_id=instance.id, uploader_id=instance.writer_id, file=file)
            bulk_list.append(doctor_file)
        DoctorFile.objects.bulk_create(bulk_list)


class NewPrescription(NewAbstract):
    """
    ONLY CREATE
    """

    def __init__(self, invoker):
        self.invoker = invoker
        self.old_instance = invoker.prescription
        self.is_update = invoker.is_update
        self.status = False

        self.validate_status()

    def validate_status(self):
        if not self.is_update:
            is_doctor = self.invoker.writer.user_type.doctor
            if is_doctor:
                self.status = True
        elif self.is_update:
            self.status = True
        else:
            raise AuthenticationFailed

    def execute(self):
        validated_data = self.invoker.validated_data
        if self.is_update:
            self.update_prescription(validated_data)
        else:
            doctor = self.invoker.writer.doctor
            self.create_prescription(doctor, validated_data)

    def create_prescription(self, doctor, validated_data):
        self.invoker.prescription = Prescription.objects.create(writer=doctor, **validated_data)

    def update_prescription(self, validated_data):
        Prescription.objects.filter(id=self.old_instance.id).update(**validated_data)
        self.old_instance.refresh_from_db()


class NewFilePrescriptions(NewAbstract):
    """
    CREATE OR UPDATE
    """

    def __init__(self, invoker):
        self.start_date = invoker.start_date
        self.end_date = invoker.end_date
        self.instance = invoker.prescription
        self.is_update = invoker.is_update
        self.status = False

        self.validate_status()

    def validate_status(self):
        try:
            if self.start_date < self.end_date:
                self.status = True
        except TypeError:
            self.status = False

    def execute(self):
        if self.is_update:
            self.delete_old_instance_for_update()
        self.create_file_prescriptions(self.instance.id, self.start_date, self.end_date)

    def delete_old_instance_for_update(self):
        self.instance.file_prescriptions.update(deleted=True)

    def create_file_prescriptions(self, prescription_id, start_date, end_date):
        import datetime
        bulk_list = (
            FilePrescription(
                prescription_id=prescription_id,
                day_number=day_number + 1,
                date=start_date + datetime.timedelta(days=day_number))
            for day_number in range((end_date - start_date).days + 1))
        FilePrescription.objects.bulk_create(bulk_list)


class PrescriptionInvoker:
    def __init__(self, validated_data, update=False):
        self.writer = validated_data.pop('writer', None)
        self.start_date = validated_data.get('start_date', None)
        self.end_date = validated_data.get('end_date', None)
        self.upload_files = validated_data.pop('doctor_upload_files', None)
        self.validated_data = validated_data

        self.is_update = update
        self.prescription = None


class UpdateSupporterSerailzier(PrescriptionModelSerializer):
    @transaction.atomic
    def update(self, instance: Prescription, validated_data: Dict[str, Any]):
        invoker = PrescriptionInvoker(validated_data, update=True)
        invoker.prescription = instance

        for extra_class in [NewPrescription, NewFiles, NewFilePrescriptions]:
            extra_instance = extra_class(invoker)
            if extra_instance.status:
                extra_instance.execute()
        return invoker.prescription


class CreateSupporterSerializer(PrescriptionModelSerializer):
    @transaction.atomic
    def create(self, validated_data: Dict[str, Any]):
        invoker = PrescriptionInvoker(validated_data)

        for extra_class in [NewPrescription, NewFiles, NewFilePrescriptions]:
            extra_instance = extra_class(invoker)
            if extra_instance.status:
                extra_instance.execute()
        return invoker.prescription


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
    doctor_upload_files = serializers.ListField(child=serializers.FileField(), write_only=True)

    class Meta:
        model = Prescription
        fields = ['url', 'writer', 'status', 'description', 'doctor_upload_files', 'doctor_files',
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

    class Meta:
        model = Prescription
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
