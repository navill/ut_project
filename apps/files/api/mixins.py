from __future__ import annotations

from typing import Type

from django.db.models import QuerySet


class QuerySetMixin:
    def get_queryset(self) -> Type[QuerySet]:
        user = self.request.user
        queryset = super().get_queryset()
        if user.is_doctor:
            queryset = queryset.select_doctor().select_prescription(). \
                filter_prescription_writer(user)
        elif user.is_patient:
            queryset = queryset.select_patient().select_file_prescription().filter_uploader(user)
        return queryset if user.is_superuser else queryset

    # def _get_user_role(self, user):
    #     if user.is_doctor:
    #         query = 'uploader__doctor'
    #     elif user.is_patient:
    #         query = 'uploader__patient'
    #     return query
