import pytest


def test_create_hospital(hospital):
    assert hospital.country == '대한민국'
    assert hospital.city == '광주'
    assert hospital.name == '한국병원'


def test_create_department(department):
    assert department.medical_center.name == '한국병원'
    assert department.name == '정신의학과'


def test_create_major(major):
    assert major.department.medical_center.name == '한국병원'
    assert major.department.name == '정신의학과'
    assert major.name == '정신의학'

