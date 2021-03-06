from typing import TYPE_CHECKING, NoReturn, Dict, Tuple, Union

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import permissions
from rest_framework_simplejwt.settings import api_settings

from accounts.api.utils import PostProcessingUserDirector
from accounts.models import BaseUser

if TYPE_CHECKING:
    from accounts.api.authentications import CustomRefreshToken

User = get_user_model()


class SignupSerializerMixin:
    def create(self, validated_data: Dict[str, str]):
        user_data = validated_data.pop('user')
        try:
            with transaction.atomic():
                baseuser = User.objects.create_user(**user_data)
                user = self.Meta.model.objects.create(user_id=baseuser.id, **validated_data)
                director = PostProcessingUserDirector(user=user, baseuser=baseuser)
                director.build_user_group_and_permission()
        except Exception:
            raise
        return user


class RefreshBlacklistMixin:
    def try_blacklist(self, refresh: 'CustomRefreshToken') -> NoReturn:
        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    refresh.blacklist()
                except AttributeError:
                    pass

    def set_refresh_payload(self, refresh: 'CustomRefreshToken') -> NoReturn:
        refresh.set_jti()
        refresh.set_exp()

    def set_user_expired_to(self, epoch_time: int) -> NoReturn:
        user = self.context['request'].user
        user.set_token_expired(epoch_time)


class PermissionMixin:
    def is_safe_method(self, request) -> bool:
        return request.method in permissions.SAFE_METHODS

    def is_superuser(self, request) -> bool:
        return request.user.is_superuser

    def is_authenticated(self, request) -> bool:
        return request.user.is_authenticated

    def is_owner(self, request, obj) -> bool:
        user = request.user
        owner_id = None

        if hasattr(obj, 'user'):  # 체크하고자 하는 객체의 소유자(user)
            owner_id = obj.user if isinstance(obj.user, int) else obj.user.id
        return user.is_superuser or bool(user.id == owner_id)

    def has_group(self, request, group_name: str) -> bool:
        if not self.is_authenticated(request):
            return False

        user = request.user
        user_type = user.user_type

        if user_type is not None:
            return getattr(user.user_type, group_name)
        else:
            return user.groups.filter(name=group_name).exists()

    def is_related(self, request, obj) -> bool:
        user = request.user
        id_field = ''
        if user.user_type.doctor:
            id_field = 'doctor_id'
        elif user.user_type.patient:
            id_field = 'patient_id'

        return hasattr(obj, id_field)


class UserTypeForAuthMixin:
    def set_user_type(self, results: Union[Tuple, None]):
        if self._validate(results):
            user, _ = results
            _ = self.get_typed_user(user)

    def get_typed_user(self, user: User) -> User:
        group_name = self._get_group_name(user)
        user.set_user_type(group_name)
        return user

    def _validate(self, results):
        if isinstance(results, Tuple) and isinstance(results[0], BaseUser):
            return True
        else:
            raise Exception('invalid user')

    def _get_group_name(self, user: User) -> str:
        group_list = user.groups.values_list('name')
        if group_list:
            return list(user.groups.values_list('name', flat=True))[0]
