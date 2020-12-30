from django.db import transaction

from accounts.models import BaseUser
from accounts.utils import UserPostProcessor


class UserCreateMixin:
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        try:
            with transaction.atomic():
                baseuser = BaseUser.objects.create_user(**user_data)
                user = self.Meta.model.objects.create(user=baseuser, **validated_data)

                user_processor = UserPostProcessor(user=user, baseuser=baseuser)
                user_processor.set_group_and_permission()
        except Exception:
            raise
        return user
