from typing import NoReturn, Type

from django.db.models import QuerySet
from django_filters.fields import Lookup
from django_filters.rest_framework import FilterSet, CharFilter, NumberFilter, LookupChoiceFilter
from rest_framework.exceptions import ValidationError

from accounts.models import Patient, Doctor
from config.utils.filter_backends import create_extra_expression


class DoctorFilter(FilterSet):
    major_id = NumberFilter(field_name='major_id', label='major pk')
    full_name = CharFilter(field_name='full_name', label='full name')
    major_name = CharFilter(field_name='major_name', label='major name')
    department_name = CharFilter(field_name='department_name', label='department name')
    medical_center_name = CharFilter(field_name='medical_center_name', label='medical center name')

    class Meta:
        model = Doctor
        fields = ['full_name', 'major_id', 'major_name', 'department_name', 'medical_center_name']


class CustomLookupChoiceFilter(LookupChoiceFilter):
    def validate_value(self, value: str) -> NoReturn:
        try:
            value = int(value)
        except Exception:
            raise ValidationError(f"'{value}' can not be converted to integer")


class AgeLookupChoiceFilter(CustomLookupChoiceFilter):
    def filter(self, qs: Type[QuerySet], lookup: Lookup) -> QuerySet:
        if not lookup:
            return super().filter(qs, None)

        self.lookup_expr = lookup.lookup_expr
        self.validate_value(lookup.value)
        expression = create_extra_expression({self.lookup_expr: lookup.value})
        return qs.add_extra_for_age(expression)


class AgeRangeLookupChoiceFilter(CustomLookupChoiceFilter):
    def filter(self, qs: Type[QuerySet], lookup: Lookup) -> QuerySet:
        if not lookup:
            return super().filter(qs, None)

        self.lookup_expr = lookup.lookup_expr
        min_age, max_age = lookup.value.replace(' ', '').split('-')
        for age in min_age, max_age:
            self.validate_value(age)

        expression = create_extra_expression({'lte': max_age, 'gte': min_age})
        return qs.add_extra_for_age(expression)


class PatientFilter(FilterSet):
    user_id = NumberFilter(field_name='user_id', label='user id')
    full_name = CharFilter(field_name='full_name', label='full name')
    doctor_name = CharFilter(field_name='doctor_name', label='doctor name')
    doctor_id = NumberFilter(field_name='doctor_id', label='doctor id')
    age = AgeLookupChoiceFilter(
        field_class=NumberFilter.field_class,
        field_name='age',
        lookup_choices=[
            ('exact', 'Equals'),
            ('gte', 'Greater than'),
            ('lte', 'Less than')
        ], label='환자의 나이')
    age_range = AgeRangeLookupChoiceFilter(
        field_class=CharFilter.field_class,
        field_name='age',
        lookup_choices=[
            ('exact', 'Equals')
        ], label='환자 나이 범위 검색(ex: 10-20)'
    )

    class Meta:
        model = Patient
        fields = ['full_name', 'doctor_name', 'doctor_id', 'user_id', 'age', 'age_range']  # + ['disease_code]
