import datetime
from typing import Dict, NoReturn

from dateutil.relativedelta import relativedelta
from django.db.models import QuerySet
from django_filters.rest_framework import FilterSet, CharFilter, NumberFilter
from rest_framework.exceptions import ValidationError

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

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        super().__init__(data=data, queryset=queryset, request=request, prefix=prefix)
        self._validation_age_data(data)

    def filter_min_age(self, queryset: QuerySet, name: str, value: int) -> QuerySet:
        max_birth_date = self._get_calculated_birth(name, value)
        return queryset.filter(birth__lte=max_birth_date)

    def filter_max_age(self, queryset: QuerySet, name: str, value: int) -> QuerySet:
        min_birth_date = self._get_calculated_birth(name, value)
        return queryset.filter(birth__gte=min_birth_date)

    def _get_calculated_birth(self, name: str, age: int) -> datetime.date:
        extra_number = 0
        if name == 'max_age':
            extra_number = 1
        calculated_year = datetime.datetime.now() - relativedelta(years=age + extra_number)
        calculated_result = calculated_year + relativedelta(days=extra_number)

        return calculated_result.date()

    def _validation_age_data(self, data: Dict[str, str]) -> NoReturn:
        try:
            if int(data.get('min_age')) > int(data.get('max_age')):
                raise ValidationError("'max_age' must be greater than or equal to 'min_age'")
        except ValueError:  # 두 값중 하나라도 입력값이 없을(또는 빈 문자열)경우 -> pass
            pass
