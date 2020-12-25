def test_create_doctor(create_doctor_with_group):
    user, doctor = create_doctor_with_group
    assert user.username == 'doctortest'
    assert user.groups.filter(name='doctor').exists()
    assert user.is_doctor
    assert user.full_name == 'doctor lastname'
    assert user.pk == 1
    assert doctor.pk == 1
    assert doctor.get_absolute_url() == '/accounts/doctors/1'


def test_create_patient(create_patient_with_group):
    user, patient = create_patient_with_group
    assert user.username == 'patienttest'
    assert user.groups.filter(name='patient').exists()
    assert user.full_name == 'patient lastname'
    assert user.is_patient
    assert patient.pk == 2
    assert patient.user_doctor.pk == 1
    assert patient.get_absolute_url() == '/accounts/patients/2'
