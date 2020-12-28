import pytest

from hospitals.models import MedicalCenter, Department, Major


@pytest.fixture
def hospital(db):
    data = {
        'country': 'KOREA',
        'city': 'GWANGJU',
        'name': '한국병원',
        'address': '광주 광역시 ...',
        'postal_code': '12345',
        'main_call': '062-111-1111',
        'sub_call': '062-222-2222'
    }
    medical_object = MedicalCenter.objects.create(**data)
    return medical_object


@pytest.fixture
def department(hospital):
    data = {
        'medical_center': hospital,
        'name': '정신의학과',
        'call': '062-333-3333'
    }
    department_object = Department.objects.create(**data)
    return department_object


@pytest.fixture
def major(department):
    data = {
        'department': department,
        'name': '정신의학',
        'call': '062-444-4444'
    }
    major_object = Major.objects.create(**data)
    return major_object


li = ['한국병원', '서울병원', '광주병원']
data = {
    'country': 'KOREA',
    'city': 'GWANGJU',
    'name': '한국병원',
    'address': '광주 광역시 ...',
    'postal_code': '12345',
    'main_call': '062-111-1111',
    'sub_call': '062-222-2222',
}
