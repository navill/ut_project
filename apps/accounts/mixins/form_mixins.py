import itertools
import sys
from typing import TYPE_CHECKING, Union, Dict

from django.apps import apps
from django.contrib.auth.models import Group
from django.db import transaction
from django.db.models import Q

if TYPE_CHECKING:
    from accounts.models import BaseUser, NormalUser, StaffUser


# baseuser.post_save() 시그널 사용이 더 나을지?
class UserSaveForm:
    @transaction.atomic
    def save(self):
        user = super().save(commit=False)  # save = UserCreationForm
        user, role = self._set_role_for_baseuser(user=user)
        user.save()  # save = AbstractBaseUser
        self._create_user_with_groups(user=user, role=role)
        return user

    def _set_role_for_baseuser(self, user: 'BaseUser'):
        role = self._get_role()
        self._set_role(user, role)
        return user, role

    def _set_role(self, user: 'BaseUser' = None, role=None):
        # todo: apply try excpet
        setattr(user, 'is_' + role.lower(), True)

    def _get_role(self):
        return self.__class__.__name__.split('SignUpForm')[0]

    def _create_user_with_groups(self, user: 'BaseUser' = None, role: str = None):
        user_class = self._get_user_class(role)
        cleaned_data = self._get_fields_without_baseuser()
        self._add_user_to_group(user=user, groupname=role)

        # create staff or normal user
        user_class.objects.create(user=user, **cleaned_data)

    def _get_user_class(self, role: str = None) -> Union['StaffUser', 'NormalUser']:
        class_name = ''.join([role, 'User'])
        return apps.get_model('accounts', class_name)

    def _get_fields_without_baseuser(self) -> Dict[str, str]:
        return dict(itertools.islice(self.cleaned_data.items(), 3, sys.maxsize))

    def _add_user_to_group(self, user: 'BaseUser' = None, groupname=None):
        group, _ = Group.objects.get_or_create(name=groupname.lower())
        user.groups.add(group)


class Grouping:
    """
    create_group
    link_group_permissions

    """
    pass


class CommonUserQuerySetMixin:
    def active(self):
        return self.filter(user__is_active=True)

    def staff(self):
        return self.filter(Q(user__is_staff=True) & Q(user__is_normal=False))

    def normal(self):
        return self.filter(Q(user__is_staff=False) & Q(user__is_normal=True))

    def ordered(self):
        return self.order_by('-user__date_joined')



