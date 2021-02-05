from abc import abstractmethod

from django.utils.decorators import classproperty

COMMON_USER_BASEFIELD = ('first_name', 'last_name', 'gender', 'created_at')
COMMON_PRESCRIPTION_FIELD = ('description', 'updated_at')

DOCTOR_BASEFIELD = ('user', 'major') + COMMON_USER_BASEFIELD
DOCTOR_OPTION_FIELD = ('address', 'phone', 'description')

PATIENT_BASEFIELD = ('user', 'doctor', 'age') + COMMON_USER_BASEFIELD
PATIENT_OPTION_FIELD = ('address', 'phone', 'emergency_call')

PRESCRIPTION_BASEFIELD = ('id', 'writer', 'patient', 'status', 'checked', 'created_at')
PRESCRIPTION_OPTION_FIELD = COMMON_PRESCRIPTION_FIELD + ('start_date', 'end_date')

FILEPRESCRIPTION_BASEFIELD = ('id', 'prescription', 'uploaded', 'day', 'created_at')
FILEPRESCRIPTION_OPTION_FIELD = COMMON_PRESCRIPTION_FIELD + ('day_number', 'active')


class RootField:
    @abstractmethod
    def base(self):
        raise NotImplementedError

    @abstractmethod
    def list_field(self):
        raise NotImplementedError

    @abstractmethod
    def detail_field(self):
        raise NotImplementedError


class DoctorFields(RootField):
    @classproperty
    def base(self) -> tuple:
        return DOCTOR_BASEFIELD

    @classproperty
    def all(self) -> tuple:
        return self.detail_field + ('updated_at',)

    @classproperty
    def list_field(self) -> tuple:
        return self.base

    @classproperty
    def detail_field(self) -> tuple:
        return self.base + DOCTOR_OPTION_FIELD


class PatientFields(RootField):
    @classproperty
    def base(self) -> tuple:
        return PATIENT_BASEFIELD

    @classproperty
    def all(self) -> tuple:
        return self.detail_field + ('updated_at',)

    @classproperty
    def list_field(self) -> tuple:
        return self.base

    @classproperty
    def detail_field(self) -> tuple:
        return self.base + PATIENT_OPTION_FIELD


class PrescriptionFields(RootField):
    @classproperty
    def all(self) -> tuple:
        return self.detail_field  # + @

    @classproperty
    def base(self) -> tuple:
        return PRESCRIPTION_BASEFIELD

    @classproperty
    def list_field(self) -> tuple:
        return self.base

    @classproperty
    def detail_field(self) -> tuple:
        return self.base + PRESCRIPTION_OPTION_FIELD


class FilePrescriptionFields(RootField):
    @classproperty
    def base(self) -> tuple:
        return FILEPRESCRIPTION_BASEFIELD

    @classproperty
    def list_field(self) -> tuple:
        return self.base

    @classproperty
    def detail_field(self) -> tuple:
        return self.base + FILEPRESCRIPTION_OPTION_FIELD


class CoreSerializerFields:
    doctor = DoctorFields()
    patient = PatientFields()
    prescription = PrescriptionFields()
    file_prescription = FilePrescriptionFields()
