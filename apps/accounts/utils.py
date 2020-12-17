from typing import TYPE_CHECKING

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

if TYPE_CHECKING:
    from accounts.models import BaseUser


class UserAuthenticationHandler:
    def __init__(self, user=None, baseuser=None):
        self.user = user
        self.baseuser = baseuser
        self.role = None
        self.permissions = None

    def set_group_and_permission(self):
        self.set_role(self.user)
        self.set_permissions()
        self.add_user_to_group()
        self.grant_permission_to_baseuser()

    def set_permissions(self):
        content_type_query = self._create_content_types()
        self.permissions = Permission.objects.filter(content_type_query)

    def add_user_to_group(self):
        group, created = Group.objects.get_or_create(name=self.role)
        if created:
            group.permissions.set(self.permissions)
        self.baseuser.groups.add(group)

    def grant_permission_to_baseuser(self):
        self.baseuser.user_permissions.set(self.permissions)

    def set_role(self, user: "BaseUser"):
        self.role = user.__class__.__name__.lower()

    def _create_query_as_role(self, role: str) -> "Q":
        model_query = Q(model=role)  # doctor? patient?
        if self.role == 'doctor':  # 의사일 경우 perscription 모델에 대한 권한 추가
            model_query |= Q(model='prescription')
        return model_query

    def _create_content_types(self):
        model_query = self._create_query_as_role(self.role)
        content_type_query = Q()
        content_types = ContentType.objects.filter(model_query, app_label='accounts')
        # if content_types.count() > 1:
        #     for content in content_types:
        #         content_type_query |= Q(content_type=content)
        # else:
        #     content_type_query = Q(content_type=content_types.first())
        for content in content_types:
            content_type_query |= Q(content_type=content)
        return content_type_query
