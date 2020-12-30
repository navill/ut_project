import itertools
import sys
from typing import TYPE_CHECKING, Union, Dict

from django.apps import apps
from django.contrib.auth.models import Group
from django.db import transaction
from django.db.models import Q

if TYPE_CHECKING:
    from accounts.models import BaseUser, Doctor, Patient


class UserSaveMixin:
    @transaction.atomic
    def save(self) -> 'BaseUser':
        base_user = super().save(commit=False)  # save = UserCreationForm
        base_user.save()  # save = AbstractBaseUser
        self._create_user_with_groups(user=base_user)
        return base_user

    def _create_user_with_groups(self, user: 'BaseUser' = None):
        user_type = self._get_type()  # Staff
        user_class = self._get_user_class(user_type=user_type)  # StaffUser
        cleaned_data = self._get_fields_excluding_baseuser()  # StaffUser.department
        self._add_user_to_group(user=user, groupname=user_type)

        user_class.objects.create(user=user, **cleaned_data)

    def _get_type(self) -> str:
        return self.__class__.__name__.split('SignUpForm')[0]

    def _get_user_class(self, user_type=None) -> Union['Doctor', 'Patient']:
        return apps.get_model('accounts', user_type)

    def _get_fields_excluding_baseuser(self) -> Dict[str, str]:
        return dict(itertools.islice(self.cleaned_data.items(), 3, sys.maxsize))

    def _add_user_to_group(self, user: 'BaseUser' = None, groupname: str = None):
        group, created = Group.objects.get_or_create(name=groupname.lower())
        user.groups.add(group)


class CommonUserQuerySetMixin:
    def active(self):
        return self.filter(user__is_active=True)

    def filt_doctor(self):
        return self.filter(Q(is_doctor=True) & Q(is_patient=False))

    def filt_patient(self):
        return self.filter(Q(is_doctor=False) & Q(is_patient=True))

    def ordered(self, value='-user__date_created'):
        return self.order_by(value)
