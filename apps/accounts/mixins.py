import importlib
import itertools
import sys
from typing import TYPE_CHECKING, Union, Dict

from django.contrib.auth.models import Group
from django.db.models import Q

if TYPE_CHECKING:
    from accounts.models import BaseUser, NormalUser, StaffUser


class UserFormMixin:
    def create_user_with_groups(self, user: 'BaseUser' = None):
        role = self._get_role()
        user_class = self._get_user_class(role)
        cleaned_data = self._extract_valid_fields()
        user_class.objects.create(user=user, **cleaned_data)

        self._add_user_to_group(user=user, groupname=role.lower())

    def set_role(self, user: 'BaseUser' = None):
        raise NotImplementedError('must be implemented in subclass')

    def _add_user_to_group(self, user: 'BaseUser' = None, groupname=None):
        group, _ = Group.objects.get_or_create(name=groupname)
        user.groups.add(group)

    def _get_role(self):
        return self.__class__.__name__.split('SignUpForm')[0]

    def _get_user_class(self, role) -> Union['StaffUser', 'NormalUser']:
        class_name = ''.join([role, 'User'])
        my_module = importlib.import_module("accounts.models")
        return getattr(my_module, class_name)

    def _extract_valid_fields(self) -> Dict[str, str]:
        return dict(itertools.islice(self.cleaned_data.items(), 3, sys.maxsize))


class CommonUserQuerySetMixin:
    def active(self):
        return self.filter(user__is_active=True)

    def staff(self):
        return self.filter(Q(user__is_staff=True) & Q(user__is_normal=False))

    def normal(self):
        return self.filter(Q(user__is_staff=False) & Q(user__is_normal=True))

    def ordered(self):
        return self.order_by('-user__date_joined')
