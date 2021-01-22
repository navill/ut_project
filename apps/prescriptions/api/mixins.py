from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from django.db.models import QuerySet


class CurrentUserRelatedFieldMixin:
    def filter_current_user_by(self, attribute_name: str) -> Optional['QuerySet']:
        request = self.context.get('request', None)
        queryset = super().get_queryset()
        if not request or not queryset:
            return None
        query = {attribute_name: request.user}
        return queryset.filter(**query)
