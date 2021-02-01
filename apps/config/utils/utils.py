from django.db.models import F, Value
from django.db.models.functions import Concat


def concatenate_name(target_field: str = None) -> Concat:
    first_name = 'first_name'
    last_name = 'last_name'
    if target_field:
        first_name = f'{target_field}__{first_name}'
        last_name = f'{target_field}__{last_name}'
    full_name = Concat(F(first_name), Value(' '), F(last_name))
    return full_name
