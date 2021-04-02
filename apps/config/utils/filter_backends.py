from typing import Dict

from django_filters.rest_framework import DjangoFilterBackend

LOOKUP_OPERATOR = {
    'exact': '=',
    'lte': '<=',
    'gte': '>='
}


def create_extra_expression(target_expressions: Dict[str, int]) -> str:
    expr_container = []
    function_name = 'django_mysql.calculate_age(birth)'

    for name, value in target_expressions.items():
        expr_container.append(f"{function_name} {LOOKUP_OPERATOR[name]} {value}")

    extra_expression = f"{expr_container[0]} AND {expr_container[1]}" if len(expr_container) == 2 \
        else expr_container[0]

    return extra_expression


class CustomDjangoFilterBackend(DjangoFilterBackend):
    pass
