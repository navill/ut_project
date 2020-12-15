from rest_framework.generics import RetrieveUpdateAPIView, ListCreateAPIView

from accounts.api.permissions import OnlyDoctor
from prescriptions.api.serializers import BasePrescriptionSerializer
from prescriptions.models import Prescription


# [GET, POST]/prescriptions
class PrescriptionListCreateAPIView(ListCreateAPIView):
    queryset = Prescription.objects.all()
    serializer_class = BasePrescriptionSerializer
    permission_classes = [OnlyDoctor]

    def perform_create(self, serializer):
        serializer.save(writer=self.request.user)


# [GET, PUT] /prescriptions/<slug>
class PrescriptionRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Prescription.objects.all()
    serializer_class = BasePrescriptionSerializer
    permission_classes = [OnlyDoctor]

    def perform_create(self, serializer):
        serializer.save(writer=self.request.user)
