from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import RetrieveAPIView, CreateAPIView, UpdateAPIView

from accounts.api.permissions import IsDoctor, IsOwner, RelatedPatientReadOnly, IsPatient
from prescriptions import docs
from prescriptions.api.serializers import (PrescriptionCreateSerializer,
                                           FilePrescriptionListSerializer,
                                           FilePrescriptionCreateSerializer,
                                           PrescriptionListSerializer,
                                           PrescriptionDetailSerializer,
                                           FilePrescriptionDetailSerializer,
                                           FilePrescriptionUpdateSerializer,
                                           PrescriptionUpdateSerializer)
from prescriptions.api.utils import CommonListAPIView
from prescriptions.models import Prescription, FilePrescription


class PrescriptionListAPIView(CommonListAPIView):
    queryset = Prescription.objects.select_all().prefetch_doctor_file()
    serializer_class = PrescriptionListSerializer
    permission_classes = [IsDoctor | IsPatient]
    lookup_field = 'pk'

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Prescription.objects.none()
        return super().get_queryset()

    @swagger_auto_schema(**docs.prescription_list)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class PrescriptionCreateAPIView(CreateAPIView):
    queryset = Prescription.objects.select_all().prefetch_doctor_file()
    serializer_class = PrescriptionCreateSerializer
    permission_classes = []

    @swagger_auto_schema(**docs.prescription_create)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class PrescriptionRetrieveAPIView(RetrieveAPIView):
    queryset = Prescription.objects.select_all()
    serializer_class = PrescriptionDetailSerializer
    permission_classes = [IsOwner | RelatedPatientReadOnly]
    lookup_field = 'pk'

    @swagger_auto_schema(**docs.prescription_detail)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class PrescriptionUpdateAPIView(UpdateAPIView):
    queryset = Prescription.objects.select_all()
    serializer_class = PrescriptionUpdateSerializer
    permission_classes = [IsOwner]
    lookup_field = 'pk'

    @swagger_auto_schema(**docs.prescription_update)
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(**docs.prescription_update)
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class FilePrescriptionListAPIView(CommonListAPIView):
    queryset = FilePrescription.objects.all()
    serializer_class = FilePrescriptionListSerializer
    permission_classes = [IsDoctor | IsPatient]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Prescription.objects.none()
        return super().get_queryset()

    @swagger_auto_schema(**docs.file_prescription_list)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class FilePrescriptionCreateAPIView(CreateAPIView):
    queryset = FilePrescription.objects.all()
    serializer_class = FilePrescriptionCreateSerializer
    permission_classes = [IsDoctor]

    @swagger_auto_schema(**docs.file_prescription_create)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class FilePrescriptionRetrieveAPIView(RetrieveAPIView):
    queryset = FilePrescription.objects.all()
    serializer_class = FilePrescriptionDetailSerializer
    permission_classes = [IsOwner | RelatedPatientReadOnly]
    lookup_field = 'pk'

    @swagger_auto_schema(**docs.file_prescription_detail)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class FilePrescriptionUpdateAPIView(UpdateAPIView):
    queryset = FilePrescription.objects.all()
    serializer_class = FilePrescriptionUpdateSerializer
    permission_classes = [IsOwner]
    lookup_field = 'pk'

    @swagger_auto_schema(**docs.file_prescription_update)
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(**docs.file_prescription_update)
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
