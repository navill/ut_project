from typing import NoReturn

from django.db.models import QuerySet
from django_filters.rest_framework import FilterSet, NumberFilter, DateFilter, CharFilter, BooleanFilter, ChoiceFilter
from rest_framework.exceptions import ValidationError

from prescriptions.models import Prescription, HealthStatus


class PrescriptionFilter(FilterSet):
    writer_id = NumberFilter(field_name='writer', label='작성자(의사) 계정의 pk')
    writer_name = CharFilter(field_name='writer_name', label='작성자(의사)의 이름')
    patient_id = NumberFilter(field_name='patient', label='소견서의 대상이 되는 환자 계정의 pk')
    patient_name = CharFilter(field_name='patient_name', label='환자의 이름')
    checked = BooleanFilter(field_name='checked')
    status = ChoiceFilter(choices=HealthStatus.choices)
    created_at = DateFilter(label='소견서 작성일', method='filter_created_at')
    min_date = DateFilter(label='파일 업로드 시작일', method='filter_min_date')
    max_date = DateFilter(label='파일 업로드 종료일', method='filter_max_date')
    ordering = CharFilter(method='filter_ordering', label='정렬할 필드 이름')

    class Meta:
        model = Prescription
        fields = ['writer_id', 'writer_name', 'patient_id', 'patient_name', 'min_date', 'max_date', 'created_at',
                  'checked', 'status', 'ordering']

    def filter_created_at(self, queryset: QuerySet, name: str, value: str) -> QuerySet:
        return queryset.filter(created_at__date=value)

    def filter_min_date(self, queryset: QuerySet, name: str, value: str) -> QuerySet:
        return queryset.filter(start_date__gte=value)

    def filter_max_date(self, queryset: QuerySet, name: str, value: str) -> QuerySet:
        return queryset.filter(end_date__lte=value)

    def filter_ordering(self, queryset: QuerySet, name: str, value: str) -> QuerySet:
        self._validate_query_param(value)
        ordered_queryset = queryset.order_by(value)
        return ordered_queryset

    def _validate_query_param(self, value: str) -> NoReturn:
        field_name_list = []
        for field in self.queryset.model._meta.fields:
            field_name_list.append(field.name)
        if value[1:] in field_name_list or value in field_name_list:
            pass
        else:
            raise ValidationError(f"can not use '{value}' at ordering param")

# class FilePrescriptionFilter(FilterSet):
#     class Meta:
#         model = FilePrescription
#         fields = []
#
