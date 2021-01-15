from typing import TYPE_CHECKING, Union

from rest_framework.generics import RetrieveUpdateAPIView, ListCreateAPIView
from rest_framework.serializers import Serializer

from accounts.api.permissions import IsDoctor, IsOwner, RelatedPatientReadOnly, IsPatient
from prescriptions.api import serializers
from prescriptions.models import Prescription

if TYPE_CHECKING:
    from django.db.models import QuerySet


class PrescriptionListCreateAPIView(ListCreateAPIView):
    queryset = Prescription.objects.select_all().defer_option_fields()
    serializer_class = serializers.PrescriptionSerializer
    permission_classes = [IsDoctor | IsPatient]
    lookup_field = 'pk'

    def get_queryset(self) -> Union["QuerySet", None]:
        queryset = super().get_queryset()

        user = self.request.user

        if user.is_doctor:
            return queryset.filter_writer(writer_id=user.id)
        elif user.is_patient:
            return queryset.filter_patient(patient_id=user.id)
        else:
            return queryset if user.is_superuser else None


class PrescriptionRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Prescription.objects.select_all().defer_option_fields()
    serializer_class = serializers.PrescriptionSerializer
    permission_classes = [IsOwner | RelatedPatientReadOnly]
    lookup_field = 'pk'

    def perform_update(self, serializer: Serializer):
        serializer.save()
