from typing import Type, Optional, TYPE_CHECKING

from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

from accounts.api.serializers import RawDoctorSerializer
from accounts.models import Patient
from files.api.serializers import PatientUploadedFileListSerializer, DoctorFileInPrescriptionSerializer
from prescriptions.api.mixins import PrescriptionSerializerMixin
from prescriptions.models import Prescription, HealthStatus, FilePrescription

if TYPE_CHECKING:
    from django.db.models import QuerySet


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


class DefaultPrescriptionSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='prescriptions:detail-update',
                                               lookup_field='pk')
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
    writer = RawDoctorSerializer(read_only=True)
    patient = FilteredPrimaryKeyRelatedField(queryset=Patient.objects.select_all(),
                                             write_only=True, target_field='doctor_id')
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    checked = serializers.BooleanField(default=False)

    writer_name = serializers.SerializerMethodField(read_only=True)
    patient_name = serializers.SerializerMethodField(read_only=True)

    class Meta(DefaultPrescriptionSerializer.Meta):
        fields = DefaultPrescriptionSerializer.Meta.fields + ['writer_name', 'patient_name',
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


class PrescriptionCreateSerializer(PrescriptionSerializerMixin, serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='prescriptions:prescription-detail-update',
        lookup_field='pk'
    )
    writer = serializers.HiddenField(default=CurrentUserDefault())
    patient = FilteredPrimaryKeyRelatedField(queryset=Patient.objects.select_all(),
                                             write_only=True, target_field='doctor_id')
    doctor_files = DoctorFileInPrescriptionSerializer(many=True, read_only=True)
    upload_doctor_files = serializers.ListField(child=serializers.FileField(), write_only=True)
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    checked = serializers.BooleanField(default=False)

    class Meta(DefaultPrescriptionSerializer.Meta):
        fields = DefaultPrescriptionSerializer.Meta.fields + ['doctor_files', 'start_date', 'end_date', 'status',
                                                              'checked', 'url', 'upload_doctor_files']


class FilePrescriptionSerializer(PrescriptionSerializerMixin, serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='prescriptions:file-prescription-detail-update',
        lookup_field='pk'
    )
    description = serializers.CharField(default='')
    status = serializers.ChoiceField(choices=HealthStatus.choices)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(read_only=True)
    prescription = serializers.PrimaryKeyRelatedField(read_only=True)
    day_number = serializers.IntegerField(read_only=True)
    day = serializers.DateField(read_only=True)
    active = serializers.BooleanField()
    uploaded = serializers.BooleanField()
    checked = serializers.BooleanField()

    class Meta:
        model = FilePrescription
        fields = ['url', 'id', 'prescription', 'description', 'status', 'day_number', 'day', 'deleted', 'active',
                  'uploaded', 'checked', 'created_at', 'updated_at']


class FilePrescriptionListSerializer(FilePrescriptionSerializer):
    pass


class FilePrescriptionCreateSerializer(FilePrescriptionSerializer):
    prescription = serializers.PrimaryKeyRelatedField(queryset=Prescription.objects.select_all())
    active = serializers.BooleanField(read_only=True)
    uploaded = serializers.BooleanField(read_only=True)
    checked = serializers.BooleanField(read_only=True)

    class Meta(FilePrescriptionSerializer.Meta):
        fields = FilePrescriptionSerializer.Meta.fields


class FilePrescriptionRetrieveUpdateSerializer(FilePrescriptionSerializer):
    active = serializers.BooleanField(read_only=True)
    uploaded = serializers.BooleanField(read_only=True)
    checked = serializers.BooleanField()

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
