from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class HistoryMixin:
    def get_queryset(self):
        return super().get_queryset().filter_prescription_writer(self.request.user.id)

# [Deprecated]
# class CurrentUserRelatedFieldMixin:
#     def filter_current_user_by(self, attribute_name: str) -> Optional['QuerySet']:
#         request = self.context.get('request', None)
#         queryset = super().get_queryset()
#         if not request or not queryset:
#             return None
#         query = {attribute_name: request.user}
#         return queryset.filter(**query)
