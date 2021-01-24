from rest_framework import serializers

from accounts.api.serializers import (PatientSerializer, CoreDoctorSerializer, CorePatientSerializer)
from files.api.serializers import DoctorFileSerializer, PatientFileSerializer
from prescriptions.api.serializers import (PrescriptionSerializer, FilePrescriptionSerializer)

"""
login
[POST]/login
logout
[GET]/logout

doctor main
#0 - [GET]/doctors/<int:pk>/patients
- [GET]/patients
- [GET]/doctors/<int:pk>

#1 - [GET]/doctors/<int:pk>/patients/<int:pk>/prescriptions
- [GET]/patients/<int:pk>
- [GET]/prescriptions

#2 - [GET]/prescription-nested-files/<int:pk>/file-prescriptions
- [GET]/prescriptions/<int:pk>
- [GET]/datafiles/doctor-files
- [GET]/prescriptions/file-pres

#3 - [GET]…/prescriptions/<int:pk>/file-pres/<int:pk>/patient-files

doctor update
[PATCH]…/doctors/<int:pk>


"""


# 0
class DoctorNestedPatientSerializer(CoreDoctorSerializer):
    patients = PatientSerializer(many=True)

    class Meta(CoreDoctorSerializer.Meta):
        fields = CoreDoctorSerializer.Meta.fields


# 1
class PatientNestedPrescriptionSerializer(CorePatientSerializer):
    prescriptions = PrescriptionSerializer(many=True)

    class Meta(PatientSerializer.Meta):
        fields = PatientSerializer.Meta.fields + ['prescriptions']


class DoctorUpdateSerializer(serializers.ModelSerializer):
    pass


class PrescriptionNestedDoctorFileSerializer(PrescriptionSerializer):
    doctor_files = DoctorFileSerializer(many=True)

    class Meta(PrescriptionSerializer.Meta):
        fields = PrescriptionSerializer.Meta.fields + ['doctor_files']


# 2
class PrescriptionNestedFilePrescriptionSerializer(PrescriptionNestedDoctorFileSerializer):
    file_prescriptions = FilePrescriptionSerializer(many=True)

    class Meta(PrescriptionSerializer.Meta):
        fields = PrescriptionSerializer.Meta.fields + ['file_prescriptions']


# 3  /file-prescription/<int:pk>/patient-files
class FilePrescriptionNestedPatientFileSerializer(FilePrescriptionSerializer):
    prescription = PrescriptionNestedDoctorFileSerializer()
    patient_files = PatientFileSerializer(many=True)

    class Meta(FilePrescriptionSerializer.Meta):
        fields = FilePrescriptionSerializer.Meta.fields + ['prescription', 'patient_files']
