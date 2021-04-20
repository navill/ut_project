import datetime
from abc import ABCMeta, abstractmethod
from typing import Type, Optional, TYPE_CHECKING, Any, Dict, NoReturn, Union, List, Tuple

from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.fields import CurrentUserDefault

from accounts.models import Patient, Doctor
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


class PrescriptionDirector:
    def __init__(self, validated_data: Dict[str, Any], is_update: bool = False):
        self.validated_data = validated_data
        self.is_update = is_update
        self.prescription = None
        self.builder_list = []

    def build(self) -> NoReturn:
        builders = [builder(self) for builder in self.builder_list]  # initialize_attr + validate
        for builder in builders:
            if builder.status:
                builder.execute()

        return self.prescription

    def set_builders(self, builders: Union[List, Tuple]) -> NoReturn:
        if isinstance(builders, list):
            if len(self.builder_list) == 0:
                self.builder_list = builders
            else:
                self.builder_list.extend(builders)
        else:
            raise TypeError


class BuilderInterface(metaclass=ABCMeta):
    prescription: Prescription or None
    director: PrescriptionDirector
    is_update: bool
    status: bool

    @abstractmethod
    def execute(self) -> NoReturn:
        raise NotImplementedError

    @abstractmethod
    def initialize_attributes(self) -> NoReturn:
        raise NotImplementedError

    @abstractmethod
    def validate_status(self) -> NoReturn:
        raise NotImplementedError


class FileBuilder(BuilderInterface):
    def __init__(self, director):
        self.director = director
        self.upload_files = None
        self.is_update = False
        self.status = False

        self.initialize_attributes()
        self.validate_status()

    def initialize_attributes(self):
        director = self.director
        self.upload_files = director.validated_data.pop('doctor_upload_files', None)
        self.is_update = director.is_update

    def validate_status(self) -> NoReturn:
        if self.upload_files:
            self.status = True
        else:
            self.status = False

    def execute(self) -> NoReturn:
        if self.is_update:
            self.delete_old_instance_for_update()
        self.create_doctor_files(self.upload_files, self.director.prescription)

    def delete_old_instance_for_update(self) -> NoReturn:
        self.director.prescription.doctor_files.update(deleted=True)

    def create_doctor_files(self, upload_files: 'InMemoryUploadedFile', instance: Prescription) -> NoReturn:
        bulk_list = []
        for file in upload_files:
            doctor_file = DoctorFile(prescription_id=instance.id, uploader_id=instance.writer_id, file=file)
            bulk_list.append(doctor_file)
        DoctorFile.objects.bulk_create(bulk_list)


class PrescriptionBuilder(BuilderInterface):
    def __init__(self, director: PrescriptionDirector):
        self.director = director
        self.writer = None
        self.is_update = False
        self.status = False
        self.initialize_attributes()
        self.validate_status()

    def initialize_attributes(self):
        director = self.director
        self.writer = director.validated_data.pop('writer', None)
        self.is_update = director.is_update

    def validate_status(self) -> NoReturn:
        if not self.is_update:
            is_doctor = self.writer.user_type.doctor
            if is_doctor:
                self.status = True

        elif self.is_update:
            self.status = True

        else:
            raise AuthenticationFailed

    def execute(self) -> NoReturn:
        validated_data = self.director.validated_data
        if self.is_update:
            self.update_prescription(validated_data)

        elif not self.is_update and self.director.prescription is None:
            doctor = self.writer.doctor
            self.create_prescription(doctor, validated_data)

        else:
            raise Exception(f'{self.__class__.__name__} can not execute.')  # ValidationError?? 어떤 에러?

    def create_prescription(self, doctor: Doctor, validated_data: Dict[str, Any]) -> NoReturn:
        self.director.prescription = Prescription.objects.create(writer=doctor, **validated_data)

    def update_prescription(self, validated_data: Dict[str, Any]) -> NoReturn:
        Prescription.objects.filter(id=self.director.prescription.id).update(**validated_data)
        self.director.prescription.refresh_from_db()


class FilePrescriptionBuilder(BuilderInterface):
    def __init__(self, director):
        self.director = director
        self.start_date = director.validated_data.get('start_date', None)
        self.end_date = director.validated_data.get('end_date', None)
        self.prescription = director.prescription
        self.is_update = False
        self.status = False
        self.initialize_attributes()
        self.validate_status()

    def initialize_attributes(self):
        director = self.director

        self.start_date = director.validated_data.get('start_date', None)
        self.end_date = director.validated_data.get('end_date', None)
        self.prescription = director.prescription
        self.is_update = director.is_update

    def validate_status(self) -> NoReturn:
        try:
            if self.start_date < self.end_date:
                self.status = True
        except TypeError:
            self.status = False

    def execute(self) -> NoReturn:
        if self.is_update:
            self.delete_old_instance_for_update()
        self.create_file_prescriptions(self.director.prescription.id, self.start_date, self.end_date)

    def delete_old_instance_for_update(self) -> NoReturn:
        file_prescription_list = []
        file_prescriptions = self.prescription.file_prescriptions.all()

        for file_prescription in file_prescriptions:
            file_prescription.deleted = True
            file_prescription_list.append(file_prescription)

        file_prescriptions.bulk_update(file_prescription_list, ['deleted'])

    def create_file_prescriptions(self, prescription_id: int, start_date: datetime, end_date: datetime) -> NoReturn:
        bulk_list = (
            FilePrescription(
                prescription_id=prescription_id,
                day_number=day_number + 1,
                date=start_date + datetime.timedelta(days=day_number))
            for day_number in range((end_date - start_date).days + 1))
        _ = FilePrescription.objects.bulk_create(bulk_list)
        self.apply_check_to_prescription()

    def apply_check_to_prescription(self):
        self.director.prescription.checked = False
        self.director.prescription.save()


class UpdateSupporterSerailzier(PrescriptionModelSerializer):
    @transaction.atomic
    def update(self, instance: Prescription, validated_data: Dict[str, Any]) -> Prescription:
        director = PrescriptionDirector(validated_data, is_update=True)
        director.set_builders([PrescriptionBuilder, FilePrescriptionBuilder, FileBuilder])
        director.prescription = instance
        director.build()
        return director.prescription


class CreateSupporterSerializer(PrescriptionModelSerializer):
    @transaction.atomic
    def create(self, validated_data: Dict[str, Any]) -> Prescription:
        director = PrescriptionDirector(validated_data)
        director.set_builders([PrescriptionBuilder, FilePrescriptionBuilder, FileBuilder])
        director.build()
        return director.prescription


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
