from django.db.models import F
from django.db.models.functions import Concat


def get_defer_fields_set(parent_field_name: str, *fields):
    return [f'{parent_field_name}__{field}' for field in fields]


def concatenate_name(target_field: str):
    full_name = Concat(F(f'{target_field}__first_name'), F(f'{target_field}__last_name'))
    return full_name
