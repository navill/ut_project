import pytest
from rest_framework.reverse import reverse

from accounts.models import Doctor, Patient
from prescriptions.models import Prescription


def test_prescriptions_stored_in_test_db(db, django_db_setup):
    prescriptions = Prescription.objects.select_all()
    prescription = Prescription.objects.first()
    assert prescription.id
    assert prescription.status in ['NORMAL', 'ABNORMAL', 'UNKNOWN']
    assert prescription.deleted is False
    assert isinstance(prescription.writer, Doctor)
    assert isinstance(prescription.patient, Patient)

    for prescription in prescriptions:
        assert prescription.id
        assert prescription.status in ['NORMAL', 'ABNORMAL', 'UNKNOWN']
        assert prescription.deleted is False
        assert isinstance(prescription.writer, Doctor)
        assert isinstance(prescription.patient, Patient)


@pytest.mark.django_db
def test_create_prescription():
    doctor = Doctor.objects.get(user_id=2)
    patient = Patient.objects.get(user_id=6)
    value = {
        "description": "created prescription",
        "status": "UNKNOWN",
        "created_at": "2021-01-04T00:00:00",
        "updated_at": "2021-01-04T00:00:00",
        "deleted": False,
        "writer": doctor,
        "patient": patient,
        "start_date": None,
        "end_date": None
    }
    obj = Prescription.objects.create(**value)
    assert obj.description == 'created prescription'


@pytest.mark.django_db
def test_create_prescription_by_view(api_client):
    # token = CustomRefreshToken.for_user(doctor.user)
    # access = token.access_token
    # api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(access))
    doctor = Doctor.objects.get(user_id=2)
    api_client.force_authenticate(user=doctor.user)
    patient = Patient.objects.get(user_id=5)
    url = reverse('prescriptions:prescription-list')

    value = {
        "description": "new test",
        "patient": patient.user_id,
        "start_date": '2021-02-01',
        "end_date": '2021-02-10'
    }
    response = api_client.post(url, data=value, format='json')
    assert response.status_code == 201
    assert response.data['description'] == "new test"
    created = Prescription.objects.last()
    assert created.description == "new test"
