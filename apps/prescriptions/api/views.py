from rest_framework.generics import RetrieveUpdateAPIView, ListCreateAPIView

from accounts.api.permissions import IsDoctor, IsOwner, RelatedPatientReadOnly, IsPatient, PatientReadOnly
from prescriptions.api import serializers
from prescriptions.models import Prescription
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models import QuerySet


# [GET, POST]/prescriptions
class PrescriptionListCreateAPIView(ListCreateAPIView):
    queryset = Prescription.objects.all()
    serializer_class = serializers.PrescriptionSerializer
    permission_classes = [IsDoctor | IsPatient]
    lookup_field = 'pk'

    def perform_create(self, serializer):
        serializer.save(writer=self.request.user)

    def get_queryset(self) -> "QuerySet":
        queryset = super().get_queryset()
        user = self.request.user
        filter_query = {"writer": user}
        if user.is_patient:
            filter_query = {"user_patient": user.patient}
        return queryset.filter(**filter_query)


# [GET, PUT] /prescriptions/<slug>
class PrescriptionRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Prescription.objects.all()
    serializer_class = serializers.PrescriptionSerializer
    permission_classes = [IsOwner | RelatedPatientReadOnly]  # obj.writer == request.user
    lookup_field = 'pk'

    def perform_update(self, serializer):
        serializer.save()
