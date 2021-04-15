import pytest

from prescriptions.models import FilePrescription, Prescription


@pytest.mark.django_db
def test_auto_check_by_updated_file_prescription():
    prescription = Prescription.objects.first()
    file_prescriptions = FilePrescription.objects.filter(prescription_id=prescription.id)
    file_prescriptions.update(checked=True)

    # file_prescription.checked=False
    first_file_prescription = file_prescriptions.first()
    first_file_prescription.checked = False
    first_file_prescription.save()
    assert first_file_prescription.checked is False
    not_checked_prescription = file_prescriptions.first().prescription
    assert not_checked_prescription.checked is False

    # file_prescriptions.checked=False
    file_prescriptions.update(checked=False)
    not_checked_prescription = file_prescriptions.first().prescription
    assert not_checked_prescription.checked is False

    # file_prescription.checked=True
    first_file_prescription.checked = True
    first_file_prescription.save()
    assert first_file_prescription.checked is True
    not_checked_prescription = first_file_prescription.prescription
    assert not_checked_prescription.checked is False

    # file_prescriptions.checked=True
    file_prescriptions.update(checked=True)
    for file_prescription in file_prescriptions:
        assert file_prescription.checked
    first_file_prescription = file_prescriptions.first()
    parent_prescription = first_file_prescription.prescription
    assert parent_prescription.checked is True
