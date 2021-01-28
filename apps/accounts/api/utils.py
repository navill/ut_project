from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Union, NoReturn, Type

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

if TYPE_CHECKING:
    from accounts.models import Patient, Doctor

User = get_user_model()


class CreatedUserPair:
    def __init__(self, user: Union['Patient', 'Doctor'], baseuser: User):
        self.user = user
        self.baseuser = baseuser
        self._model_name = None

        if self.validate_user():
            self.model_name = user
        else:
            raise ValueError('invalid user')

    @property
    def model_name(self) -> str:
        return self._model_name

    @model_name.setter
    def model_name(self, user: Union['Patient', 'Doctor']) -> NoReturn:
        self._model_name = user.__class__.__name__.lower()

    def validate_user(self) -> bool:
        if not isinstance(self.baseuser, User):
            return False
        return True


class GroupPermissionInterface(metaclass=ABCMeta):
    @abstractmethod
    def set_permissions_for_models(self) -> NoReturn:
        raise NotImplementedError("This method must be implemented in subclasses!")

    @abstractmethod
    def add_user_to_model_group(self) -> NoReturn:
        raise NotImplementedError("This method must be implemented in subclasses!")

    @abstractmethod
    def grant_permission_to_baseuser(self) -> NoReturn:
        raise NotImplementedError("This method must be implemented in subclasses!")


class GroupPermissionBuilder(GroupPermissionInterface):  # base builder pattern
    def __init__(self, pair_user: 'CreatedUserPair' = None, permissions: 'Permission' = None):
        self.pair_user = pair_user
        self.permissions = permissions

    def build(self):
        self.set_permissions_for_models()
        if self.pair_user and self.permissions:
            self.add_user_to_model_group()
            self.grant_permission_to_baseuser()
        else:
            raise Exception

    def set_permissions_for_models(self) -> NoReturn:
        queries = self._create_content_type_queries()
        self.permissions = Permission.objects.filter(queries)

    def add_user_to_model_group(self) -> NoReturn:
        group, created = Group.objects.get_or_create(name=self.pair_user.model_name)

        if created and self.permissions.exists():
            group.permissions.set(self.permissions)

        self.pair_user.baseuser.groups.add(group)

    def grant_permission_to_baseuser(self) -> NoReturn:
        self.pair_user.baseuser.user_permissions.set(self.permissions)

    def _create_content_type_queries(self) -> Q:
        queries = self._create_queries_using_model_name(self.pair_user.model_name)
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


class PostProcessingUserDirector:
    def __init__(self, user: Union['Doctor', 'Patient'] = None, baseuser: 'User' = None):
        self.created_user = CreatedUserPair(user=user, baseuser=baseuser)

    def build_user_group_and_permission(self) -> NoReturn:
        builder = GroupPermissionBuilder(pair_user=self.created_user)
        builder.build()
