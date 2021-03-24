from django_filters.rest_framework import FilterSet, CharFilter, NumberFilter
from rest_framework.exceptions import ValidationError

from accounts.models import Patient, Doctor


class DoctorFilter(FilterSet):
    major_id = NumberFilter(field_name='major_id')
    full_name = CharFilter(field_name='full_name', label='full name')
    major_name = CharFilter(field_name='major_name', label='major name')
    department_name = CharFilter(field_name='department_name', label='department name')
    medical_center_name = CharFilter(field_name='medical_center_name', label='medical center name')

    class Meta:
        model = Doctor
        fields = ['major_id', 'full_name', 'major_name', 'department_name', 'medical_center_name']


class PatientFilter(FilterSet):
    full_name = CharFilter(field_name='full_name', label='full name')
    doctor_id = NumberFilter(field_name='doctor_id', label='doctor id')
    min_age = NumberFilter(label='min age', method='filter_min_age')
    max_age = NumberFilter(label='max age', method='filter_max_age')

    # disease_code = CharFilter(field_name='disease_code')

    class Meta:
        model = Patient
        fields = ['full_name', 'doctor_id', 'min_age', 'max_age']  # + ['disease_code]

    def filter_queryset(self, queryset):
        cleaned_data = self.form.cleaned_data
        min_age = cleaned_data.pop('min_age') or 1
        max_age = cleaned_data.pop('max_age') or 999

        if min_age > max_age:
            raise ValidationError('must be minimum age less then maximum age')

        if max_age or min_age:
            queryset = queryset.filter_between_age(min_age, max_age)

        return super().filter_queryset(queryset)
