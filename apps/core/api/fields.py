from abc import ABCMeta, abstractmethod
from typing import Type

from django.utils.decorators import classproperty

COMMON_USER_BASEFIELD = ['first_name', 'last_name', 'gender', 'created_at']
COMMON_PRESCRIPTION_FIELD = ['description', 'updated_at']


class RootFields:
    @abstractmethod
    def base(self):
        raise NotImplementedError

    @abstractmethod
    def list_field(self):
        raise NotImplementedError

    @abstractmethod
    def detail_field(self):
        raise NotImplementedError

    @classmethod
    def create_child_fields(cls, fields: Type['RootFields'] = None, other_fields=None):
        pass


DOCTOR_BASEFIELD = ['user', 'major'] + COMMON_USER_BASEFIELD
DOCTOR_OPTION_FIELD = ['address', 'phone', 'description']


class DoctorFields(RootFields):
    @classproperty
    def base(self) -> list:
        return DOCTOR_BASEFIELD

    @classproperty
    def list_field(self) -> list:
        return self.base

    @classproperty
    def detail_field(self) -> list:
        return self.base + DOCTOR_OPTION_FIELD


PATIENT_BASEFIELD = ['user', 'doctor', 'age'] + COMMON_USER_BASEFIELD
PATIENT_OPTION_FIELD = ['address', 'phone', 'emergency_call']


class PatientFields(RootFields):
    @classproperty
    def all(self) -> list:
        return PATIENT_BASEFIELD + PATIENT_OPTION_FIELD + ['updated_at']

    @classproperty
    def base(self) -> list:
        return PATIENT_BASEFIELD

    @classproperty
    def list_field(self) -> list:
        return self.base

    @classproperty
    def detail_field(self) -> list:
        return self.base + PATIENT_OPTION_FIELD


PRESCRIPTION_BASEFIELD = ['id', 'writer', 'patient', 'status', 'checked', 'created_at']
PRESCRIPTION_OPTION_FIELD = COMMON_PRESCRIPTION_FIELD + ['start_date', 'end_date']


class PrescriptionFields(RootFields):
    @classproperty
    def all(self) -> list:
        return []

    @classproperty
    def base(self) -> list:
        return PRESCRIPTION_BASEFIELD

    @classproperty
    def list_field(self) -> list:
        return self.base

    @classproperty
    def detail_field(self) -> list:
        return self.base + PRESCRIPTION_OPTION_FIELD


FILEPRESCRIPTION_BASEFIELD = ['id', 'prescription', 'uploaded', 'day', 'created_at']
FILEPRESCRIPTION_OPTION_FIELD = COMMON_PRESCRIPTION_FIELD + ['day_number', 'active']


class FilePrescriptionFields(RootFields):
    @classproperty
    def base(self) -> list:
        return FILEPRESCRIPTION_BASEFIELD

    @classproperty
    def list_field(self) -> list:
        return self.base

    @classproperty
    def detail_field(self) -> list:
        return self.base + FILEPRESCRIPTION_OPTION_FIELD


class CoreSerializerFields:
    doctor = DoctorFields()
    patient = PatientFields()
    prescription = PrescriptionFields()
    file_prescription = FilePrescriptionFields()


def generate_fields(parent_fields, *child_fields):
    pass
