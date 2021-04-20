import datetime
from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, NoReturn, List

from django.db import transaction
from rest_framework.exceptions import AuthenticationFailed, ValidationError

from accounts.models import Doctor
from files.models import DoctorFile
from prescriptions.models import Prescription, FilePrescription

if TYPE_CHECKING:
    from django.core.files.uploadedfile import InMemoryUploadedFile

PRESCRIPTION_ATTRS = ['writer']  # pop
FILEPRESCRIPTION_ATTRS = ['start_date', 'end_date']  # get
DOCTORFILE_ATTRS = ['doctor_upload_files']  # pop


class PrescriptionDirector:
    def __init__(self, validated_data: Dict[str, Any], is_update: bool = False):
        self.validated_data = validated_data
        self.is_update = is_update
        self.prescription = None
        self.builder_list = []

    @transaction.atomic
    def build(self) -> NoReturn:
        self.validate_before_build()
        builders = [builder(self) for builder in self.builder_list]  # initialize_attr + validate

        for builder in builders:
            if builder.status:
                builder.execute()

        return self.prescription

    def set_builders(self, builders: List) -> NoReturn:
        self.validate_builders(builders)
        if len(self.builder_list) == 0:
            self.builder_list = builders
        else:
            self.builder_list.extend(builders)

    def validate_before_build(self):
        if len(self.builder_list) == 0:
            raise ValidationError("'builder_list' should not be empty")

        if self.builder_list[0] != PrescriptionBuilder:
            raise ValidationError("'PrescriptionBuilder' must be placed in the first")

    def validate_builders(self, builders):
        if not isinstance(builders, list):
            raise ValidationError("argument 'builders' must be list type")

        if len(builders) == 0:
            raise ValidationError("'set_builders()' arguments must be list of builder classes")


class BuilderInterface(metaclass=ABCMeta):
    prescription: Prescription or None
    director: PrescriptionDirector
    is_update: bool
    status: bool

    @abstractmethod
    def execute(self) -> NoReturn:
        raise NotImplementedError

    @abstractmethod
    def initialize_attributes(self) -> NoReturn:
        raise NotImplementedError

    @abstractmethod
    def validate_builder(self) -> NoReturn:
        raise NotImplementedError


class FileBuilder(BuilderInterface):
    def __init__(self, director):
        self.director = director
        self.doctor_upload_files = None
        self.is_update = False
        self.status = False

        self.initialize_attributes()
        self.validate_builder()

    def initialize_attributes(self):
        director = self.director
        for attr in DOCTORFILE_ATTRS:
            setattr(self, attr, director.validated_data.pop(attr, None))
        self.is_update = director.is_update

    def validate_builder(self) -> NoReturn:
        if self.doctor_upload_files:
            self.status = True
        else:
            self.status = False

    def execute(self) -> NoReturn:
        if self.is_update:
            self.delete_old_instance_for_update()
        self.create_doctor_files(self.doctor_upload_files, self.director.prescription)

    def delete_old_instance_for_update(self) -> NoReturn:
        self.director.prescription.doctor_files.update(deleted=True)

    def create_doctor_files(self, upload_files: 'InMemoryUploadedFile', instance: Prescription) -> NoReturn:
        bulk_list = []
        for file in upload_files:
            doctor_file = DoctorFile(prescription_id=instance.id, uploader_id=instance.writer_id, file=file)
            bulk_list.append(doctor_file)
        DoctorFile.objects.bulk_create(bulk_list)


class PrescriptionBuilder(BuilderInterface):
    def __init__(self, director: PrescriptionDirector):
        self.director = director
        self.writer = None
        self.is_update = False
        self.status = False
        self.initialize_attributes()
        self.validate_builder()

    def initialize_attributes(self):
        director = self.director
        for attr in PRESCRIPTION_ATTRS:
            setattr(self, attr, director.validated_data.pop(attr, None))
        self.is_update = director.is_update

    def validate_builder(self) -> NoReturn:
        if not self.is_update:
            is_doctor = self.writer.user_type.doctor
            if is_doctor:
                self.status = True
            else:
                raise AuthenticationFailed

        elif self.is_update:
            self.status = True

    def execute(self) -> NoReturn:
        validated_data = self.director.validated_data
        if self.is_update:
            self.update_prescription(validated_data)
        else:
            doctor = self.writer.doctor
            self.create_prescription(doctor, validated_data)

    def create_prescription(self, doctor: Doctor, validated_data: Dict[str, Any]) -> NoReturn:
        self.director.prescription = Prescription.objects.create(writer=doctor, **validated_data)

    def update_prescription(self, validated_data: Dict[str, Any]) -> NoReturn:
        Prescription.objects.filter(id=self.director.prescription.id).update(**validated_data)
        self.director.prescription.refresh_from_db()


class FilePrescriptionBuilder(BuilderInterface):
    def __init__(self, director):
        self.director = director
        self.start_date = None
        self.end_date = None
        self.is_update = False
        self.status = False
        self.initialize_attributes()
        self.validate_builder()

    def initialize_attributes(self):
        director = self.director
        for attr in FILEPRESCRIPTION_ATTRS:
            setattr(self, attr, director.validated_data.get(attr, None))
        self.is_update = director.is_update

    def validate_builder(self) -> NoReturn:
        try:
            if self.start_date < self.end_date:
                self.status = True
        except TypeError:
            self.status = False

    def execute(self) -> NoReturn:
        if self.is_update:
            self.delete_old_instance_for_update()
        self.create_file_prescriptions(self.director.prescription.id, self.start_date, self.end_date)

    def delete_old_instance_for_update(self) -> NoReturn:
        file_prescription_list = []
        file_prescriptions = self.director.prescription.file_prescriptions.all()

        for file_prescription in file_prescriptions:
            file_prescription.deleted = True
            file_prescription_list.append(file_prescription)

        file_prescriptions.bulk_update(file_prescription_list, ['deleted'])

    def create_file_prescriptions(self, prescription_id: int, start_date: datetime, end_date: datetime) -> NoReturn:
        bulk_list = (
            FilePrescription(
                prescription_id=prescription_id,
                day_number=day_number + 1,
                date=start_date + datetime.timedelta(days=day_number))
            for day_number in range((end_date - start_date).days + 1))
        _ = FilePrescription.objects.bulk_create(bulk_list)
        self.apply_check_to_prescription()

    def apply_check_to_prescription(self):
        self.director.prescription.checked = False
        self.director.prescription.save()
