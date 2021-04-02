from django.db.models import QuerySet
from rest_framework.pagination import LimitOffsetPagination

from accounts.models import AccountsModel


class FasterPagination(LimitOffsetPagination):
    def get_count(self, queryset: QuerySet) -> int:
        id_field = 'id'
        try:
            if issubclass(queryset.model, AccountsModel):
                id_field = 'user_id'
            return queryset.values(id_field).count()
            # return queryset.count()
        except (AttributeError, TypeError):
            return len(queryset)
