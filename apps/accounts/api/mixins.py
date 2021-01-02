from typing import TYPE_CHECKING

from django.db import transaction
from rest_framework import permissions
from rest_framework_simplejwt.settings import api_settings

from accounts.models import BaseUser
from accounts.api.utils import CreatedUser, PostProcessingUserDirector

if TYPE_CHECKING:
    from accounts.api.authentications import CustomRefreshToken


class UserCreateMixin:
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        try:
            with transaction.atomic():
                baseuser = BaseUser.objects.create_user(**user_data)
                user = self.Meta.model.objects.create(user=baseuser, **validated_data)

                created_user = CreatedUser(user=user, baseuser=baseuser)
                director = PostProcessingUserDirector(created_user=created_user)
                director.build_user_group_and_permission()

        except Exception:
            raise
        return user


class RefreshBlacklistMixin:
    def try_blacklist(self, refresh: 'CustomRefreshToken'):
        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    refresh.blacklist()
                except AttributeError:
                    pass

    def set_refresh_payload(self, refresh: 'CustomRefreshToken'):
        refresh.set_jti()
        refresh.set_exp()

    def set_user_expired_to(self, epoch_time: int):
        user = self.context['request'].user
        user.set_token_expired(epoch_time)


class PermissionMethodBundleMixin:
    def is_safe_method(self, request) -> bool:
        return request.method in permissions.SAFE_METHODS

    def is_superuser(self, request) -> bool:
        return request.user.is_superuser

    def is_authenticated(self, request) -> bool:
        return request.user.is_authenticated

    def is_owner(self, request, obj) -> bool:
        user = request.user
        owner = None
        if hasattr(obj, 'user'):
            owner = obj.user
        elif hasattr(obj, 'writer'):
            owner = obj.writer
        return bool(user == owner)

    # hasattr(self, request.user, 'doctor') vs request.user.groups.filter(name='doctor').exists()
    def has_group(self, request, group_name: str) -> bool:
        return hasattr(request.user, group_name)
