from typing import TYPE_CHECKING, Union

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from accounts.models import AccountsModel, BaseUser

if TYPE_CHECKING:
    from accounts.models import Patient, Doctor


class CreatedUser:
    def __init__(self, user: Union['Patient', 'Doctor'], baseuser: 'BaseUser'):
        self.user = user
        self.baseuser = baseuser
        self._model_name = None

        if self.validate_user():
            self.set_model_name()
        else:
            raise ValueError('invalid user')

    def set_model_name(self):
        self._model_name = self.user.__class__.__name__.lower()

    @property
    def model_name(self):
        return self._model_name

    def validate_user(self):
        if not isinstance(self.user, AccountsModel) or not isinstance(self.baseuser, BaseUser):
            return False
        return True


class GroupPermissionBuilder:
    def __init__(self):
        self.target_user = None
        self.permissions = None

    def set_permissions_for_models(self):
        queries = self._create_content_type_queries()
        self.permissions = Permission.objects.filter(queries)

    def add_user_to_model_group(self):
        group, created = Group.objects.get_or_create(name=self.target_user.model_name)

        if created and self.permissions.exists():
            group.permissions.set(self.permissions)

        self.target_user.baseuser.groups.add(group)

    def grant_permission_to_baseuser(self):
        self.target_user.baseuser.user_permissions.set(self.permissions)

    def _create_content_type_queries(self) -> Q:
        queries = self._create_queries_using_model_name(self.target_user.model_name)
        content_type_query = Q()
        content_types = ContentType.objects.filter(queries, app_label='accounts')

        if not content_types.exists():
            raise ContentType.DoesNotExist('not found ContentType object')

        for content in content_types:
            content_type_query |= Q(content_type=content)
        return content_type_query

    def _create_queries_using_model_name(self, model_name: str) -> Q:
        query = Q(model=model_name)
        if model_name == 'doctor':
            query |= Q(model='prescription')  # 의사일 경우 perscription 모델에 대한 권한이 필요함
        return query


class PostProcessingDirector:
    def __init__(self, created_user: 'CreatedUser'):
        self.created_user = created_user
        self.builder = GroupPermissionBuilder()

    def construct_builder(self):
        self.builder.target_user = self.created_user
        self.builder.set_permissions_for_models()
        self.builder.add_user_to_model_group()
        self.builder.grant_permission_to_baseuser()
