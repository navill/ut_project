from typing import Type, Optional, TYPE_CHECKING, Any, Dict

from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

from accounts.models import Patient
from core.api.fields import PrescriptionFields, FilePrescriptionFields
from files.api.serializers import DoctorFileInPrescriptionSerializer
from files.models import DoctorFile
from prescriptions.api.serializers.patterns import (PrescriptionDirector, PrescriptionBuilder, FilePrescriptionBuilder,
                                                    FileBuilder)
from prescriptions.models import Prescription, FilePrescription

if TYPE_CHECKING:
    from django.db.models import QuerySet


class PrescriptionModelSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='prescriptions:prescription-detail',
        lookup_field='pk',
        read_only=True
    )

    class Meta:
        model = Prescription
        fields = ['url']


class UpdateSupporterSerailzier(PrescriptionModelSerializer):
    def update(self, instance: Prescription, validated_data: Dict[str, Any]) -> Prescription:
        director = PrescriptionDirector(validated_data, is_update=True)
        director.set_builders([PrescriptionBuilder, FilePrescriptionBuilder, FileBuilder])
        director.prescription = instance
        director.build()
        return director.prescription


class CreateSupporterSerializer(PrescriptionModelSerializer):
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
        self.target_field: str = target_field

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


class PrescriptionDetailSerializer(PrescriptionModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='prescriptions:prescription-update',
        lookup_field='pk',
    )

    class Meta:
        model = Prescription
        fields = ['url'] + PrescriptionFields.detail_field

    def get_fields(self):
        ret = super().get_fields()
        request = self.context['request']

        if request.user.user_type.patient or request.user.groups.filter(name='patient').exists():
            ret.pop('url')
        return ret


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
