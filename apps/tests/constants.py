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
    u'email': 'test@test.com',
    u'password': 'test12345'
}
USER_PATIENT = {
    u'email': 'patient@test.com',
    u'password': 'test12345'
}

USER_DOCTOR = {
    u'email': 'doctor@test.com',
    u'password': 'test12345'
}
DOCTOR = {
    u'first_name': 'firstdoctor',
    u'last_name': 'lastdoctor',
    u'address': '광주광역시 어디어디..',
    u'phone': '010-111-1111',
    u'description': '의사입니다.'
}

PATIENT = {
    u'first_name': 'firstpatient',
    u'last_name': 'lastpatient',
    u'address': '광주광역시 어디어디..',
    u'phone': '010-3333-3333',
    u'age': 30,
    u'emergency_call': '010-119'
}

DATAFILE = {
    u'id': None,
    u'prescription': None,
    u'uploader': None,
    u'file': MEDIA_ROOT + '/test_file.md',
    u'checked': True,
    u'status': HealthStatus.NORMAL
}

User = get_user_model()
