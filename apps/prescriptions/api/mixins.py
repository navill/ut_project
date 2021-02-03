from typing import TYPE_CHECKING, Optional, Dict, Any, NoReturn

from django.db import transaction

from files.models import DoctorFile, PatientFile
from prescriptions.models import Prescription

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.core.files.uploadedfile import InMemoryUploadedFile


class HistoryMixin:
    def get_queryset(self):
        return super().get_queryset().filter_prescription_writer(self.request.user.id)


class CurrentUserRelatedFieldMixin:
    def filter_current_user_by(self, attribute_name: str) -> Optional['QuerySet']:
        request = self.context.get('request', None)
        queryset = super().get_queryset()
        if not request or not queryset:
            return None
        query = {attribute_name: request.user}
        return queryset.filter(**query)


class PrescriptionSerializerMixin:
    @transaction.atomic
    def create(self, validated_data: Dict[str, Any]):
        field_name = 'doctor_upload_files'
        files = validated_data.pop(field_name, None)

        if files is None:
            raise ValueError(f"'{field_name}' field must be not empty")

        prescription = self._create_prescription(validated_data)
        self._create_doctor_files(prescription.writer_id, prescription.id, files)
        return prescription

    def _create_prescription(self, validated_data: Dict[str, Any]) -> 'Prescription':
        writer = validated_data.pop('writer').doctor
        return Prescription.objects.create(writer=writer, **validated_data)

    def _create_doctor_files(self, writer_id: int,
                             prescription_id: int,
                             request_files: 'InMemoryUploadedFile') -> NoReturn:
        uploader_id = writer_id
        for file in request_files:
            DoctorFile.objects.create(uploader_id=uploader_id, prescription_id=prescription_id, file=file)
