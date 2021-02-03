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


class CommonPrescriptionSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        fields = ['description', 'status', 'checked', 'created_at', 'updated_at', 'deleted']


class OriginalPrescriptionSerializer(CommonPrescriptionSerializer):
    class Meta:
        model = Prescription
        fields = ['id', 'writer', 'patient', 'start_date', 'end_date'] + CommonPrescriptionSerializer.Meta.fields


class OriginalFilePrescriptionSerializer(CommonPrescriptionSerializer):
    class Meta:
        model = FilePrescription
        fields = ['id', 'prescription', 'day_number', 'day', 'active',
                  'uploaded'] + CommonPrescriptionSerializer.Meta.fields


class PrescriptionSerializer(OriginalPrescriptionSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='prescriptions:prescription-detail-update',
        lookup_field='pk'
    )
    writer = RawDoctorSerializer(read_only=True)
    patient = FilteredPrimaryKeyRelatedField(queryset=Patient.objects.select_all(),
                                             write_only=True, target_field='doctor_id')

    class Meta(OriginalPrescriptionSerializer.Meta):
        fields = OriginalPrescriptionSerializer.Meta.fields


class PrescriptionCreateSerializer(PrescriptionSerializerMixin, serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='prescriptions:prescription-detail-update',
        lookup_field='pk'
    )
    writer = serializers.HiddenField(default=CurrentUserDefault())
    patient = FilteredPrimaryKeyRelatedField(queryset=Patient.objects.select_all(),
                                             write_only=True, target_field='doctor_id')
    doctor_files = DoctorFileInPrescriptionSerializer(many=True, read_only=True)
    doctor_upload_files = serializers.ListField(child=serializers.FileField(), write_only=True)
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    checked = serializers.BooleanField(default=False)

    class Meta(OriginalPrescriptionSerializer.Meta):
        fields = ['url'] + OriginalPrescriptionSerializer.Meta.fields + ['doctor_files', 'doctor_upload_files']


class FilePrescriptionSerializer(serializers.ModelSerializer):
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
