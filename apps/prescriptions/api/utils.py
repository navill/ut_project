from typing import Tuple, Type, Dict

from django.db.models import F, QuerySet
from django.db.models.functions import Concat
from rest_framework.generics import ListAPIView


class CommonListAPIView(ListAPIView):
    def get_queryset(self) -> Type[QuerySet]:
        queryset = super().get_queryset()
        if self.request.user.is_superuser:
            return queryset
        return self.filter_currentuser(queryset)

    def filter_currentuser(self, queryset: QuerySet) -> Type[QuerySet]:
        expression = self.create_query_expression(queryset)
        return queryset.filter(**expression)

    def create_query_expression(self, queryset: QuerySet) -> Dict[str, int]:
        user = self.request.user
        sub_field_name = ''
        target_field = ''

        if hasattr(queryset.model, 'prescription'):
            sub_field_name = 'prescription__'

        if user.is_doctor:
            target_field = f'{sub_field_name}writer_id'
        elif user.is_patient:
            target_field = f'{sub_field_name}patient_id'

        return {target_field: user.id}


def get_defer_fields_set(parent_field_name: str, *fields: Tuple[str]):
    return [f'{parent_field_name}__{field}' for field in fields]


def concatenate_name(target_field: str) -> Concat:
    full_name = Concat(F(f'{target_field}__first_name'), F(f'{target_field}__last_name'))
    return full_name
