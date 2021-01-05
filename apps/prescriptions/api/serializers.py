from rest_framework import serializers

from accounts.models import Patient
from prescriptions.models import Prescription


class PrescriptionSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='prescriptions:detail-update',
        lookup_field='pk'
    )
    writer = serializers.PrimaryKeyRelatedField(read_only=True)
    user_patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    # user_patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    description = serializers.CharField()
    created = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", read_only=True)
    updated = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", read_only=True)

    class Meta:
        model = Prescription
        fields = ['url', 'writer', 'user_patient', 'description', 'created', 'updated']
