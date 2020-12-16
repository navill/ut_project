from django.db.models import QuerySet
from rest_framework.generics import RetrieveUpdateAPIView, ListCreateAPIView

from accounts.api.permissions import IsDoctor, IsOwner, RelatedPatientReadOnly
from prescriptions.api import serializers
from prescriptions.models import Prescription


# [GET, POST]/prescriptions
class PrescriptionListCreateAPIView(ListCreateAPIView):
    queryset = Prescription.objects.all()
    serializer_class = serializers.PrescriptionSerializer
    permission_classes = [IsDoctor]
    lookup_field = 'pk'

    def perform_create(self, serializer):
        serializer.save(writer=self.request.user)

    def get_queryset(self) -> "QuerySet":
        queryset = super().get_queryset()
        doctor = self.request.user
        return queryset.filter(writer=doctor)


# [GET, PUT] /prescriptions/<slug>
class PrescriptionRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Prescription.objects.all()
    serializer_class = serializers.PrescriptionSerializer
    permission_classes = [IsOwner | RelatedPatientReadOnly]  # obj.writer == request.user?
    lookup_field = 'pk'

    def perform_create(self, serializer):
        serializer.save(writer=self.request.user)
