import importlib
import itertools
import sys
from typing import TYPE_CHECKING, Union, Dict

from django.contrib.auth.models import Group
from django.db import transaction
from django.db.models import Q

if TYPE_CHECKING:
    from accounts.models import BaseUser, NormalUser, StaffUser


class UserSaveForm:
    @transaction.atomic
    def save(self):
        user = super().save(commit=False)  # save = UserCreationForm
        user, role = self._pre_save_baseuser_as_role(user=user)
        user.save()  # save = AbstractBaseUser
        self._create_user_with_groups(user=user, role=role)

    def _pre_save_baseuser_as_role(self, user: 'BaseUser'):
        role = self._get_role_to_pre_save()
        self._set_role_to_pre_save(user, role)
        return user, role

    def _set_role_to_pre_save(self, user: 'BaseUser' = None, role=None):
        # todo: apply try excpet
        setattr(user, 'is_' + role.lower(), True)

    def _get_role_to_pre_save(self):
        return self.__class__.__name__.split('SignUpForm')[0]

    def _create_user_with_groups(self, user: 'BaseUser' = None, role: str = None):
        user_class = self._get_user_class(role)
        cleaned_data = self._extract_valid_fields()
        self._add_user_to_group(user=user, groupname=role)

        # create staff or normal user
        user_class.objects.create(user=user, **cleaned_data)

    def _get_user_class(self, role: str = None) -> Union['StaffUser', 'NormalUser']:
        class_name = ''.join([role, 'User'])
        my_module = importlib.import_module("accounts.models")
        return getattr(my_module, class_name)

    def _extract_valid_fields(self) -> Dict[str, str]:
        return dict(itertools.islice(self.cleaned_data.items(), 3, sys.maxsize))

    def _add_user_to_group(self, user: 'BaseUser' = None, groupname=None):
        group, _ = Group.objects.get_or_create(name=groupname.lower())
        user.groups.add(group)


class CommonUserQuerySetMixin:
    def active(self):
        return self.filter(user__is_active=True)

    def staff(self):
        return self.filter(Q(user__is_staff=True) & Q(user__is_normal=False))

    def normal(self):
        return self.filter(Q(user__is_staff=False) & Q(user__is_normal=True))

    def ordered(self):
        return self.order_by('-user__date_joined')
