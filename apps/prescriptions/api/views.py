from rest_framework.generics import RetrieveUpdateAPIView, ListCreateAPIView

from accounts.api.permissions import IsDoctor, IsOwner, RelatedPatientReadOnly, IsPatient, PatientReadOnly
from prescriptions.api import serializers
from prescriptions.models import Prescription
from typing import TYPE_CHECKING, Union

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

    def get_queryset(self) -> Union["QuerySet", None]:
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_doctor:
            return queryset.filter_writer(writer=user)
        elif user.is_patient:
            return queryset.filter_patient(user_patient=user)
        else:
            return None


# [GET, PUT] /prescriptions/<slug>
class PrescriptionRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Prescription.objects.all()
    serializer_class = serializers.PrescriptionSerializer
    permission_classes = [IsOwner | RelatedPatientReadOnly]  # obj.writer == request.user
    lookup_field = 'pk'

    def perform_update(self, serializer):
        serializer.save()
