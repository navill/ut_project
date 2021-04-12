from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Union, NoReturn

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

if TYPE_CHECKING:
    from accounts.models import Patient, Doctor

User = get_user_model()


class UserPair:
    def __init__(self, user: Union['Patient', 'Doctor'], baseuser: User):
        self.user = user
        self.baseuser = baseuser
        self._user_model_name = None

        if self.validate_user():
            self.user_model_name = user
        else:
            raise ValueError('invalid user')

    @property
    def user_model_name(self) -> str:
        return self._user_model_name

    @user_model_name.setter
    def user_model_name(self, user: Union['Patient', 'Doctor']) -> NoReturn:
        model_name = user.__class__.__name__.lower()
        if model_name not in ('patient', 'doctor'):
            raise AttributeError(f'{model_name} is invalid model name')
        self._user_model_name = model_name

    def validate_user(self) -> bool:
        if not isinstance(self.baseuser, User):
            return False
        return True


"""
Builder Pattern 
- 하나의 객체를 여러 단계로 나누어 작성해야하고(baseuser 생성->grouping->permission 부여), 
각 단계를 구성하는 내용이 다른 출력(doctor or patient)을 요구할 때 사용
Client(accounts.api.mixins.SignupSerializerMixin)
- 실제 명령을 내리는 대상: 손님
Director(PostProcessingUserDirector)
- 명령을 수집하는 대상: 알바생
Builder(GroupPermissionBuilder)
- 명령을 실행하는 대상: (햄버거를 제조하는)알바생
"""


class GroupPermissionInterface(metaclass=ABCMeta):
    @abstractmethod
    def build(self) -> NoReturn:
        raise NotImplementedError("This method must be implemented in subclasses!")

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
        group, created = Group.objects.get_or_create(name=self.pair_user.user_model_name)

        if created and self.permissions.exists():
            group.permissions.set(self.permissions)

        self.pair_user.baseuser.groups.add(group)

    def grant_permission_to_baseuser(self) -> NoReturn:
        self.pair_user.baseuser.user_permissions.set(self.permissions)

    def _create_content_type_queries(self) -> Q:
        queries = self._create_queries_using_model_name(self.pair_user.user_model_name)
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
        self.created_user = UserPair(user=user, baseuser=baseuser)

    def build_user_group_and_permission(self) -> NoReturn:
        builder = GroupPermissionBuilder(pair_user=self.created_user)
        builder.build()

# [Deprecated]
# def calculate_birthdate(min_age: int, max_age: int) -> List[datetime.date]:
#     ages = [min_age, max_age]
#
#     result_date = []
#
#     for number, age in enumerate(ages):
#         calculated_year = datetime.datetime.now() - relativedelta(years=age + number)
#         calculated_age = calculated_year.date() + relativedelta(day=calculated_year.day + number)
#         result_date.append(calculated_age)
#
#     result_date.sort()  # 나이 많은 사람의 생년월일(min_date) 순서로 정렬
#     return result_date
