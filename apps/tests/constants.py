from django.contrib.auth import get_user_model

from config.settings.local import MEDIA_ROOT
from files.models import HealthStatus

DOCTOR_PARAMETER = 'user, first_name, last_name, address, phone, description, status_code', [
    ({
         'email': 'doctor@test.com',  # 201
         'password': 'test12345',
         'password2': 'test12345',
     }, 'first_doctor', 'last_doctor', '광주어딘가..', '010-111-1111', '의사입니다.', 201),
    ({
         'email': 'doctor@test.com',  # not match password
         'first_name': 'doctor',
         'last_name': 'lastname',
         'password': 'test12345',
         'password2': 'test54321',
     }, 'first_doctor', 'last_doctor', '광주어딘가..', '010-111-1111', '의사입니다.', 400),
    ({
         'email': 'doctor@test.com',  # no password2
         'first_name': 'doctor',
         'last_name': 'lastname',
         'password': 'test12345',
         'password2': '',
     }, 'first_doctor', 'last_doctor', '광주어딘가..', '010-111-1111', '의사입니다.', 400),
    ({
         'email': 'doctor@test.com',  # no password
         'first_name': 'doctor',
         'last_name': 'lastname',
         'password': '',
         'password2': 'test12345',
     }, 'first_doctor', 'last_doctor', '광주어딘가..', '010-111-1111', '의사입니다.', 400),

]
PATIENT_PARAMETER = 'user, first_name, last_name, address, phone, age, emergency_call, status_code', [
    ({
         'email': 'patient@test.com',  # 201
         'password': 'test12345',
         'password2': 'test12345',
     }, '길동', '홍', '광주 어딘가', '010-1111-1111', 30, '010-119', 201),
    ({
         'email': 'patient@test.com',  # not match password
         'first_name': 'patient',
         'last_name': 'lastname',
         'password': 'test12345',
         'password2': 'test54321',
     }, '길동', '홍', '광주 어딘가', '010-1111-1111', 30, '010-119', 400),
    ({
         'email': 'patient@test.com',  # no password2
         'first_name': 'patient',
         'last_name': 'lastname',
         'password': 'test12345',
         'password2': '',
     }, '길동', '홍', '광주 어딘가', '010-1111-1111', 30, '010-119', 400),
    ({
         'email': 'patient@test.com',  # no password
         'first_name': 'patient',
         'last_name': 'lastname',
         'password': '',
         'password2': 'test12345',
     }, '길동', '홍', '광주 어딘가', '010-1111-1111', 30, '010-119', 400),
    ({
         'email': 'patient@test.com',  # no age
         'first_name': 'patient',
         'last_name': 'lastname',
         'password': 'test12345',
         'password2': 'test12345',
     }, '길동', '홍', '광주 어딘가', '010-1111-1111', '', '010-119', 400),
    ({
         'email': 'patient@test.com',  # no emergency_call
         'first_name': 'patient',
         'last_name': 'lastname',
         'password': 'test12345',
         'password2': 'test12345',
     }, '길동', '홍', '광주 어딘가', '010-1111-1111', 30, '', 400),
]

USER_BASEUSER = {
    'email': 'test@test.com',
    'password': 'test12345'
}
USER_PATIENT = {
    'email': 'patient@test.com',
    'password': 'test12345'
}

USER_DOCTOR = {
    'email': 'doctor@test.com',
    'password': 'test12345'
}
DOCTOR = {
    'first_name': 'firstdoctor',
    'last_name': 'lastdoctor',
    'address': '광주광역시 어디어디..',
    'phone': '010-111-1111',
    'description': '의사입니다.'
}

PATIENT = {
    'first_name': 'firstpatient',
    'last_name': 'lastpatient',
    'address': '광주광역시 어디어디..',
    'phone': '010-3333-3333',
    'age': 30,
    'emergency_call': '010-119'
}

DATAFILE = {
    'id': None,
    'prescription': None,
    'uploader': None,
    'file': MEDIA_ROOT + '/test_file.md',
    'checked': True,
    'status': HealthStatus.NORMAL
}

User = get_user_model()
