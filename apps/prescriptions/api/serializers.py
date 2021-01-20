from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

from accounts.models import Patient
from prescriptions.models import Prescription, HealthStatus, FilePrescription


class WriterFilteredPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get('request', None)
        if not request:
            return None
        return super().get_queryset().filter(user_id=request.user.id)


class PatientFilteredPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get('request', None)
        if not request:
            return None
        return super().get_queryset().filter(doctor_id=request.user.id)


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
        fields = ['url', 'writer', 'patient', 'description', 'created_at', 'updated_at']


class PrescriptionSerializer(DefaultPrescriptionSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='prescriptions:prescription-detail-update',
        lookup_field='pk'
    )
    writer = serializers.HiddenField(default=CurrentUserDefault())
    patient = PatientFilteredPrimaryKeyRelatedField(queryset=Patient.objects.select_all(),
                                                    write_only=True)

    start_date = serializers.DateField()
    end_date = serializers.DateField()
    writer_name = serializers.SerializerMethodField(read_only=True)
    patient_name = serializers.SerializerMethodField(read_only=True)

    class Meta(DefaultPrescriptionSerializer.Meta):
        fields = DefaultPrescriptionSerializer.Meta.fields + ['writer_name', 'patient_name', 'start_date', 'end_date',
                                                              'url']

    def get_writer_name(self, instance):
        if hasattr(instance, 'writer_name'):
            return instance.writer_name
        # queryset에 writer_name이 없을 수 있음(ex: create 이후 annotate 호출 전)
        return instance.writer.get_full_name()

    def get_patient_name(self, instance):
        if hasattr(instance, 'patient_name'):
            return instance.patient_name
        return instance.patient.get_full_name()

    def create(self, validated_data):
        validated_data['writer'] = validated_data['writer'].doctor
        return super().create(validated_data)


class FilePrescriptionSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='prescriptions:file-prescription-detail-update',
        lookup_field='pk'
    )
    description = serializers.CharField(default='')
    status = serializers.ChoiceField(choices=HealthStatus.choices, default=HealthStatus.NONE)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    deleted = serializers.BooleanField(default=False, read_only=True)
    prescription = serializers.PrimaryKeyRelatedField(read_only=True)
    day_number = serializers.IntegerField(read_only=True)
    active = serializers.BooleanField()
    # updated = serializers.BooleanField()
    checked = serializers.BooleanField()

    class Meta:
        model = FilePrescription
        fields = '__all__'


class FilePrescriptionListSerializer(FilePrescriptionSerializer):
    pass


class FilePrescriptionRetrieveUpdateSerializer(FilePrescriptionSerializer):
    class Meta(FilePrescriptionSerializer.Meta):
        fields = FilePrescriptionSerializer.Meta.fields
