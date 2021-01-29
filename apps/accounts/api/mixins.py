from typing import TYPE_CHECKING, NoReturn

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import permissions
from rest_framework_simplejwt.settings import api_settings

from accounts.api.utils import PostProcessingUserDirector

if TYPE_CHECKING:
    from accounts.api.authentications import CustomRefreshToken

User = get_user_model()


class SignupSerializerMixin:
    def create(self, validated_data):
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

    def set_user_expired_to(self, epoch_time: int) -> NoReturn:
        user = self.context['request'].user
        user.set_token_expired(epoch_time)


class PermissionBundleMethodMixin:
    def is_safe_method(self, request) -> bool:
        return request.method in permissions.SAFE_METHODS

    def is_superuser(self, request) -> bool:
        return request.user.is_superuser

    def is_authenticated(self, request) -> bool:
        return request.user.is_authenticated

    def is_owner(self, request, obj) -> bool:
        user = request.user
        owner_id = None

        if hasattr(obj, 'user'):
            owner_id = obj.user if isinstance(obj.user, int) else obj.user.id
        return user.is_superuser or bool(user.id == owner_id)

    def has_group(self, request, group_name: str) -> bool:
        return hasattr(request.user, group_name)

    def is_related(self, request, obj) -> bool:
        user = request.user
        value = None
        if user.is_patient:
            value = 'doctor_id'
        elif user.is_doctor:
            value = 'patient_id'

        return hasattr(obj, value)
