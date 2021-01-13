from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

from accounts.models import Patient
from prescriptions.models import Prescription


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
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.select_all().defer_fields())
    description = serializers.CharField()
    created = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", read_only=True)
    updated = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", read_only=True)

    class Meta:
        model = Prescription
        fields = ['url', 'writer', 'patient', 'description', 'created', 'updated']


class PrescriptionSerializer(DefaultPrescriptionSerializer):
    writer = serializers.HiddenField(default=CurrentUserDefault())
    patient = PatientFilteredPrimaryKeyRelatedField(queryset=Patient.objects.select_all().defer_fields(),
                                                    write_only=True)

    writer_name = serializers.SerializerMethodField(read_only=True)
    patient_name = serializers.SerializerMethodField(read_only=True)

    class Meta(DefaultPrescriptionSerializer.Meta):
        fields = DefaultPrescriptionSerializer.Meta.fields + ['writer_name', 'patient_name']

    def get_writer_name(self, instance):
        if hasattr(instance, 'writer_name'):
            return instance.writer_name
        # queryset에 writer_name이 없을 수 있음(ex: create 이후 annotate 호출 전)
        return instance.writer.get_full_name()

    def get_patient_name(self, instance):
        if hasattr(instance, 'patient_name'):
            return instance.patient_name
        return instance.patient.get_full_name()

    def validate(self, attrs):
        return attrs

    def create(self, validated_data):
        validated_data['writer'] = validated_data['writer'].doctor
        return super().create(validated_data)
