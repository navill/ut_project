from typing import Optional

from django_filters.rest_framework import FilterSet, NumberFilter, DateFilter, CharFilter, BooleanFilter, ChoiceFilter, \
    OrderingFilter, LookupChoiceFilter

from prescriptions.models import Prescription, HealthStatus, FilePrescription


class DateLookupChoiceFilter(LookupChoiceFilter):
    def __init__(self, field_name=None, lookup_choices=None, field_class=None, **kwargs):
        self.field_name: Optional[str] = field_name + '__date' if field_name else None
        super().__init__(self.field_name, lookup_choices, field_class, **kwargs)


class PrescriptionFilter(FilterSet):
    writer_id = NumberFilter(field_name='writer', label='작성자(의사) 계정의 pk')
    writer_name = CharFilter(field_name='writer_name', label='작성자(의사)의 이름')
    patient_id = NumberFilter(field_name='patient', label='소견서의 대상이 되는 환자 계정의 pk')
    patient_name = CharFilter(field_name='patient_name', label='환자의 이름')
    status = ChoiceFilter(choices=HealthStatus.choices)
    ordering = OrderingFilter(
        fields={
            'created_at': 'created_at',
        },
        field_labels={
            'created_at': '소견서 작성일',
        }
    )
    checked = BooleanFilter(field_name='checked')
    created_at = DateLookupChoiceFilter(
        field_class=DateFilter.field_class,
        field_name='created_at',
        lookup_choices=[
            ('exact', 'Equals'),
            ('gte', 'Greater than'),
            ('lte', 'Less than')
        ], label='소견서 생성일')
    start_date = LookupChoiceFilter(
        field_class=DateFilter.field_class,
        field_name='start_date',
        lookup_choices=[
            ('exact', 'Equals'),
            ('gte', 'Greater than'),
            ('lte', 'Less than')
        ], label='파일 업로드 시작일')
    end_date = LookupChoiceFilter(
        field_name='end_date',
        field_class=DateFilter.field_class,
        lookup_choices=[
            ('exact', 'Equals'),
            ('gte', 'Greater than'),
            ('lte', 'Less than')
        ], label='파일 업로드 종료일')

    class Meta:
        model = Prescription
        fields = ['writer_id', 'writer_name', 'patient_id', 'patient_name', 'start_date', 'end_date', 'created_at',
                  'checked', 'status', 'ordering']


class FilePrescriptionFilter(FilterSet):
    prescription_id = NumberFilter(field_name='prescription_id', label='소견서 객체의 pk')
    writer_id = NumberFilter(label='작성자(의사) 계정의 id')
    writer_name = CharFilter(label='작성자(의사)의 이름')
    patient_id = NumberFilter(label='환자 계정의 id')
    patient_name = CharFilter(label='환자의 이름')
    status = ChoiceFilter(field_name='status', choices=HealthStatus.choices)
    created_at = DateLookupChoiceFilter(
        field_class=DateFilter.field_class,
        field_name='created_at',
        lookup_choices=[
            ('exact', 'Equals'),
            ('gte', 'Greater than'),
            ('lte', 'Less than')
        ], label='소견서 작성일(FilePrescription은 소견서 작성시 생성됨)'
    )
    date = LookupChoiceFilter(
        field_class=DateFilter.field_class,
        field_name='date',
        lookup_choices=[
            ('exact', 'Equals'),
            ('gte', 'Greater than'),
            ('lte', 'Less than')
        ], label='파일 업로드 날짜')
    active = BooleanFilter(field_name='active', label='파일 업로드가 활성화 되었는지 표시')
    uploaded = BooleanFilter(field_name='uploaded', label='환자가 파일을 올렸는지 표시')
    checked = BooleanFilter(field_name='checked', label='의사가 환자가 올린 파일을 확인했는지 표시')
    ordering = OrderingFilter(
        fields={
            'created_at': 'created_at',
            'date': 'date'
        },
        field_labels={
            'created_at': '소견서 작성일',
            'date': '파일 업로드 날짜'
        }
    )

    class Meta:
        model = FilePrescription
        fields = ['writer_id', 'writer_name', 'patient_id', 'patient_name', 'prescription_id', 'status', 'created_at',
                  'date', 'active', 'uploaded', 'checked', 'ordering']
