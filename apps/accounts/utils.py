from typing import TYPE_CHECKING, Union

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

if TYPE_CHECKING:
    from accounts.models import BaseUser, Patient, Doctor
    from django.db.models import QuerySet


# group & permission으로 분리해야할듯?
class UserPostProcessor:  # UserPostProcessor or UserGroupPermissionHandler??
    def __init__(self, user=None, baseuser=None):
        self.user: Union['Doctor', 'Patient'] = user
        self.baseuser: 'BaseUser' = baseuser
        self.model_name: str = ''
        self.permissions: 'QuerySet' = None

    def set_group_and_permission(self):
        self.set_model_name(self.user)
        self.set_permissions_for_models()
        self.add_user_to_model_group()
        self.grant_permission_to_baseuser()

    def set_model_name(self, user: Union['Doctor', 'Patient']):
        self.model_name = user.__class__.__name__.lower()

    def set_permissions_for_models(self):
        queries = self._create_content_type_queries()
        self.permissions = Permission.objects.filter(queries)

    def add_user_to_model_group(self):
        group, created = Group.objects.get_or_create(name=self.model_name)
        if created and self.permissions.exists():
            group.permissions.set(self.permissions)
        self.baseuser.groups.add(group)

    def grant_permission_to_baseuser(self):
        self.baseuser.user_permissions.set(self.permissions)

    def _create_content_type_queries(self):
        queries = self._create_queries_using_model_name(self.model_name)
        content_type_query = Q()
        content_types = ContentType.objects.filter(queries, app_label='accounts')

        if not content_types.exists():
            raise ContentType.DoesNotExist('not found ContentType object')

        for content in content_types:
            content_type_query |= Q(content_type=content)
        return content_type_query

    def _create_queries_using_model_name(self, model_name: str) -> Q:
        query = Q(model=model_name)
        if self.model_name == 'doctor':
            query |= Q(model='prescription')  # 의사일 경우 perscription 모델에 대한 권한이 필요함
        return query
