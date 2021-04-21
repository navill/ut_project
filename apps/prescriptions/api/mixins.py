from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class HistoryMixin:
    def get_queryset(self):
        return super().get_queryset().filter_prescription_writer(self.request.user.id)
