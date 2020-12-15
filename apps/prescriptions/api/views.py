from rest_framework.generics import RetrieveUpdateAPIView, ListCreateAPIView
from rest_framework.renderers import JSONRenderer

from accounts.api.permissions import OnlyDoctor
from prescriptions.api import serializers
from prescriptions.models import Prescription


# [GET, POST]/prescriptions
class PrescriptionListCreateAPIView(ListCreateAPIView):
    queryset = Prescription.objects.all()
    serializer_class = serializers.PrescriptionSerializer
    permission_classes = [OnlyDoctor]
    lookup_field = 'pk'

    def perform_create(self, serializer):
        serializer.save(writer=self.request.user)


# [GET, PUT] /prescriptions/<slug>
class PrescriptionRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Prescription.objects.all()
    serializer_class = serializers.PrescriptionSerializer
    permission_classes = [OnlyDoctor]
    # renderer_classes = [JSONRenderer]
    lookup_field = 'pk'

    def perform_create(self, serializer):
        serializer.save(writer=self.request.user)
