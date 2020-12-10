from django.db import transaction

from accounts.models import BaseUser
from accounts.utils import UserAuthenticationHandler


class UserCreateMixin:
    @transaction.atomic
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        baseuser = BaseUser.objects.create_user(**user_data)
        user = self.Meta.model.objects.create(user=baseuser, **validated_data)

        user_authentication_handler = UserAuthenticationHandler(user=user, baseuser=baseuser)
        user_authentication_handler.set_group_and_permission()
        return user
