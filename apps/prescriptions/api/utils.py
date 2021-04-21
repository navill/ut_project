from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.db.models import F, QuerySet
from django.db.models.functions import Concat
from rest_framework.generics import ListAPIView

if TYPE_CHECKING:
    User = get_user_model()


class CommonListAPIView(ListAPIView):
    """
    CommonListAPIView: Prescription, FilePrescription에 사용되는 공통 ListAPIView
    ListView에 접근하는 계정이 환자인지 의사인지에 따라 다른 쿼리문을 생성
    """

    def get_queryset(self) -> QuerySet:
        user = self.request.user
        queryset = super().get_queryset()
        return self.filter_currentuser(queryset, user)

    def filter_currentuser(self, queryset: QuerySet, user: 'User') -> QuerySet:
        target_field = self.get_target_field(queryset, user)
        return queryset.filter(**{target_field: user.id})

    def get_target_field(self, queryset: QuerySet, user) -> str:
        prefix = 'prescription__' if hasattr(queryset.model, 'prescription') else ''
        target_field = ''
        if user.user_type:
            if user.user_type.doctor:
                target_field = f'{prefix}writer_id'
            elif user.user_type.patient:
                target_field = f'{prefix}patient_id'

        else:
            if hasattr(user, 'doctor'):
                target_field = f'{prefix}writer_id'
            elif hasattr(user, 'patient'):
                target_field = f'{prefix}patient_id'

        return target_field


def concatenate_name(target_field: str) -> Concat:
    full_name = Concat(F(f'{target_field}__last_name'), F(f'{target_field}__first_name'))
    return full_name
