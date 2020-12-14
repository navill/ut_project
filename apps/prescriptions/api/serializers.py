from collections import OrderedDict

from rest_framework import serializers

from accounts.models import Patient, BaseUser
from prescriptions.models import Prescription


class UserFilteredPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get('request', None)
        queryset = super(UserFilteredPrimaryKeyRelatedField, self).get_queryset()
        if not request or not queryset:
            return None
        return queryset.filter(family_doctor=request.user)

    # def to_representation(self, value):
    #     value = super(UserFilteredPrimaryKeyRelatedField, self).to_representation(value)
    #     print(value)
    #     return value

    def to_representation(self, value):
        pk = super().to_representation(value)
        patient = Patient.objects.get(pk=pk)
        return str(patient)

    def to_internal_value(self, data):
        print('a',type(data))
        username = super(UserFilteredPrimaryKeyRelatedField, self).to_internal_value(data)
        print(username)
        return username


class PrescriptionCommonMixin(serializers.ModelSerializer):
    writer = serializers.PrimaryKeyRelatedField(read_only=True)
    patient = UserFilteredPrimaryKeyRelatedField(queryset=Patient.objects.all())
    created = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", read_only=True)
    updated = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", read_only=True)

    class Meta:
        model = Prescription
        fields = ['writer', 'patient', 'description', 'created', 'updated']


class PrescriptionSerializer(PrescriptionCommonMixin, serializers.ModelSerializer):
    class Meta(PrescriptionCommonMixin.Meta):
        model = Prescription

    # def to_representation(self, value):
    #     value = super(PrescriptionSerializer, self).to_representation(value)
    #     print(value.get('writer'))
    #     return value


class PrescriptionListSerializer(PrescriptionCommonMixin, serializers.ModelSerializer):
    class Meta(PrescriptionCommonMixin.Meta):
        model = Prescription
