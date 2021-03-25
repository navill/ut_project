from django_filters.rest_framework import FilterSet, NumberFilter, CharFilter

from hospitals.models import Department, Major, MedicalCenter


class MedicalCenterFilter(FilterSet):
    medical_center_name = CharFilter(field_name='name', label='병원 이름')
    medical_center_id = NumberFilter(field_name='id', label='병원 객체의 pk')

    class Meta:
        model = MedicalCenter
        fields = ['medical_center_name', 'medical_center_id']


class DepartmentFilter(FilterSet):
    medical_center_name = CharFilter(field_name='medical_center__name', label='병원 이름')
    medical_center_id = NumberFilter(field_name='medical_center__id', label='병원 객체의 pk')
    department_name = CharFilter(field_name='name', label='부서 이름')
    department_id = NumberFilter(field_name='id', label='부서 객체의 pk')

    class Meta:
        model = Department
        fields = ['medical_center_name', 'medical_center_id', 'department_name', 'department_id']


class MajorFilter(FilterSet):
    department_name = CharFilter(field_name='department__name', label='부서 이름')
    department_id = NumberFilter(field_name='department__id', label='부서 객체의 pk')
    major_name = CharFilter(field_name='name', label='전공 이름')
    major_id = NumberFilter(field_name='id', label='전공 객체의 pk')

    class Meta:
        model = Major
        fields = ['department_name', 'department_id', 'major_name', 'major_id']
