import datetime

from dateutil.relativedelta import relativedelta
from django.db.models import QuerySet
from django_filters.rest_framework import FilterSet, CharFilter, NumberFilter

from accounts.models import Patient, Doctor


class DoctorFilter(FilterSet):
    major_id = NumberFilter(field_name='major_id', label='major pk')
    full_name = CharFilter(field_name='full_name', label='full name')
    major_name = CharFilter(field_name='major_name', label='major name')
    department_name = CharFilter(field_name='department_name', label='department name')
    medical_center_name = CharFilter(field_name='medical_center_name', label='medical center name')

    class Meta:
        model = Doctor
        fields = ['full_name', 'major_id', 'major_name', 'department_name', 'medical_center_name']


class PatientFilter(FilterSet):
    user_id = NumberFilter(field_name='user_id', label='user id')
    full_name = CharFilter(field_name='full_name', label='full name')
    doctor_id = NumberFilter(field_name='doctor_id', label='doctor id')

    # todo: PrescriptionFilter처럼 lookup exp 적용 가능하도록 변경해야함
    min_age = NumberFilter(label='min age', method='filter_min_age')
    max_age = NumberFilter(label='max age', method='filter_max_age')

    # disease_code = CharFilter(field_name='disease_code')

    class Meta:
        model = Patient
        fields = ['full_name', 'doctor_id', 'min_age', 'max_age', 'user_id']  # + ['disease_code]

    def filter_min_age(self, queryset: QuerySet, name: str, value: int):
        max_birth_date = self._calculate_birthdate(name, value)
        return queryset.filter(birth__lte=max_birth_date)

    def filter_max_age(self, queryset: QuerySet, name: str, value: int):
        min_birth_date = self._calculate_birthdate(name, value)
        return queryset.filter(birth__gte=min_birth_date)

    def _calculate_birthdate(self, name: str, age: int) -> datetime.date:
        extra_number = 0
        if name == 'max_age':
            extra_number = 1
        calculated_year = datetime.datetime.now() - relativedelta(years=age + extra_number)
        calculated_result = calculated_year + relativedelta(days=extra_number)

        return calculated_result.date()
