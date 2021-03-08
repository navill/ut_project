from django.db.models import Func


class CalculateAge(Func):
    function = 'calculate_age'
