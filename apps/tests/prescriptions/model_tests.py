import pytest

from accounts.models import Doctor, Patient
from prescriptions.models import FilePrescription, Prescription


def test_prescriptions_stored_in_test_db(db, django_db_setup):
    prescription = Prescription.objects.first()
    assert prescription.id
    assert prescription.status in ['NORMAL', 'ABNORMAL', 'UNKNOWN']
    assert prescription.deleted is False
    assert isinstance(prescription.writer, Doctor)
    assert isinstance(prescription.patient, Patient)

    prescriptions = Prescription.objects.select_all()
    for prescription in prescriptions:
        assert prescription.id
        assert prescription.status in ['NORMAL', 'ABNORMAL', 'UNKNOWN']
        assert prescription.deleted is False
        assert isinstance(prescription.writer, Doctor)
        assert isinstance(prescription.patient, Patient)


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
    for file_prescription in file_prescriptions:
        file_prescription.checked = False
        file_prescription.save()
    not_checked_prescription = file_prescriptions.first().prescription
    assert not_checked_prescription.checked is False

    # file_prescription.checked=True
    first_file_prescription.checked = True
    first_file_prescription.save()
    assert first_file_prescription.checked is True
    not_checked_prescription = first_file_prescription.prescription
    assert not_checked_prescription.checked is False

    # file_prescriptions.checked=True
    for file_prescription in file_prescriptions:
        file_prescription.checked = True
        file_prescription.save()
    parent_prescription_ids = set(file_prescriptions.values_list('prescription_id', flat=True))
    assert len(parent_prescription_ids) == 1  # file_prescription의 부모 id는 1개만 출력됨

    parent_prescription_id = parent_prescription_ids.pop()
    parent_prescription = Prescription.objects.get(id=parent_prescription_id)
    assert parent_prescription.checked is True
