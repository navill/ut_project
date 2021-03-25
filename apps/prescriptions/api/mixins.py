from typing import TYPE_CHECKING, Optional, Dict, Any, NoReturn

from django.db import transaction

from files.models import DoctorFile
from prescriptions.models import Prescription, FilePrescription

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.core.files.uploadedfile import InMemoryUploadedFile


class HistoryMixin:
    def get_queryset(self):
        return super().get_queryset().filter_prescription_writer(self.request.user.id)

# [Deprecated]
# class CurrentUserRelatedFieldMixin:
#     def filter_current_user_by(self, attribute_name: str) -> Optional['QuerySet']:
#         request = self.context.get('request', None)
#         queryset = super().get_queryset()
#         if not request or not queryset:
#             return None
#         query = {attribute_name: request.user}
#         return queryset.filter(**query)


class PrescriptionSerializerMixin:
    @transaction.atomic
    def create(self, validated_data: Dict[str, Any]):
        field_name = 'doctor_upload_files'
        files = validated_data.pop(field_name, None)

        prescription = self._create_prescription(validated_data)
        self._create_file_prescriptions(prescription_id=prescription.id,
                                        validated_data=validated_data)
        if files:
            self._create_doctor_files(writer_id=prescription.writer_id,
                                      prescription_id=prescription.id,
                                      request_files=files)
        return prescription

    def _create_prescription(self, validated_data: Dict[str, Any]) -> 'Prescription':
        user = validated_data.pop('writer')
        writer = user.doctor
        return Prescription.objects.create(writer=writer, **validated_data)

    def _create_doctor_files(self,
                             writer_id: int,
                             prescription_id: int,
                             request_files: 'InMemoryUploadedFile') -> NoReturn:
        uploader_id = writer_id
        for file in request_files:
            DoctorFile.objects.create(uploader_id=uploader_id, prescription_id=prescription_id, file=file)

    def _create_file_prescriptions(self, prescription_id, validated_data):
        start_date = validated_data['start_date']
        end_date = validated_data['end_date']

        import datetime
        bulk_list = (
            FilePrescription(
                prescription_id=prescription_id,
                day_number=day_number + 1,
                date=start_date + datetime.timedelta(days=day_number))
            for day_number in range((end_date - start_date).days + 1))
        FilePrescription.objects.bulk_create(bulk_list)
