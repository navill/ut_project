from rest_framework import serializers

from accounts.api.serializers import DoctorSerializer, PatientSerializer
from files.api.serializers import PatientFileSerializer, DoctorFileSerializer
from prescriptions.api.serializers import PrescriptionSerializer, FilePrescriptionSerializer


class CoreDoctorSerializer(DoctorSerializer):
    class Meta(DoctorSerializer.Meta):
        fields = DoctorSerializer.Meta.fields


class CorePatientSerializer(PatientSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='core-api:patient-with-prescriptions',
        lookup_field='pk'
    )

    class Meta(PatientSerializer.Meta):
        fields = PatientSerializer.Meta.fields


class CoreDoctorFileSerializer(DoctorFileSerializer):
    # doctor detail_(update)url
    # doctor delete_url
    class Meta(DoctorFileSerializer.Meta):
        fields = DoctorFileSerializer.Meta.fields


class CorePatientFileSerializer(PatientFileSerializer):
    # patient detail(update)_url
    # patient delete_url
    class Meta(PatientFileSerializer.Meta):
        fields = PatientFileSerializer.Meta.fields


class CorePrescriptionSerializer(PrescriptionSerializer):
    # prescription detail_(update)url
    core_url = serializers.HyperlinkedIdentityField(
        view_name='core-api:prescription-detail',
        lookup_field='pk'
    )

    class Meta(PrescriptionSerializer.Meta):
        fields = PrescriptionSerializer.Meta.fields + ['core_url']


class CoreFilePrescriptionSerializer(FilePrescriptionSerializer):
    # file prescription detail_(update)url
    core_url = serializers.HyperlinkedIdentityField(
        view_name='core-api:file-prescription-detail',
        lookup_field='pk'
    )

    class Meta(FilePrescriptionSerializer.Meta):
        fields = FilePrescriptionSerializer.Meta.fields + ['core_url']
