from rest_framework.generics import RetrieveUpdateAPIView, ListCreateAPIView

from accounts.api.permissions import IsDoctor, OnlyOwner, OnlyHasPatient
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

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(writer=self.request.user)


# [GET, PUT] /prescriptions/<slug>
class PrescriptionRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Prescription.objects.all()
    serializer_class = serializers.PrescriptionSerializer
    permission_classes = [OnlyOwner]
    lookup_field = 'pk'

    def perform_create(self, serializer):
        serializer.save(writer=self.request.user)
