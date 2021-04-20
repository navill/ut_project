from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import RetrieveAPIView, CreateAPIView, UpdateAPIView

from accounts.api.permissions import IsDoctor, IsOwner, RelatedPatientReadOnly, IsPatient, PatientReadOnly
from prescriptions import docs
from prescriptions.api.filters import PrescriptionFilter, FilePrescriptionFilter
from prescriptions.api.serializers.serializers import (PrescriptionCreateSerializer,
                                                       FilePrescriptionListSerializer,
                                                       FilePrescriptionCreateSerializer,
                                                       PrescriptionListSerializer,
                                                       PrescriptionDetailSerializer,
                                                       FilePrescriptionDetailSerializer,
                                                       FilePrescriptionUpdateSerializer,
                                                       PrescriptionUpdateSerializer,
                                                       PrescriptionChoiceSerializer,
                                                       FilePrescriptionChoiceSerializer,
                                                       )
from prescriptions.api.utils import CommonListAPIView
from prescriptions.models import Prescription, FilePrescription


class PrescriptionListAPIView(CommonListAPIView):
    queryset = Prescription.objects.all().only_list()
    serializer_class = PrescriptionListSerializer
    permission_classes = [IsDoctor | PatientReadOnly]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Prescription.objects.none()
        queryset = super().get_queryset()
        return queryset

    @swagger_auto_schema(**docs.prescription_list)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class PrescriptionCreateAPIView(CreateAPIView):
    queryset = Prescription.objects.select_all().prefetch_doctor_file()
    serializer_class = PrescriptionCreateSerializer
    permission_classes = [IsDoctor]

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
        return self.partial_update(request, *args, **kwargs)

    @swagger_auto_schema(**docs.prescription_update, deprecated=True)
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class PrescriptionChoiceAPIView(CommonListAPIView):
    queryset = Prescription.objects.choice_fields()
    serializer_class = PrescriptionChoiceSerializer
    permission_classes = [IsDoctor]
    filter_class = PrescriptionFilter

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Prescription.objects.none()
        return super().get_queryset()

    @swagger_auto_schema(**docs.prescription_choice)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


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
        return self.partial_update(request, *args, **kwargs)

    @swagger_auto_schema(**docs.file_prescription_update, deprecated=True)
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class FilePrescriptionChoiceAPIView(CommonListAPIView):
    queryset = FilePrescription.objects.all()
    serializer_class = FilePrescriptionChoiceSerializer
    permission_classes = [IsDoctor]
    filter_class = FilePrescriptionFilter

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return FilePrescription.objects.none()
        return super().get_queryset()

    @swagger_auto_schema(**docs.file_prescription_choice)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
