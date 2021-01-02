from django.db import transaction

from accounts.models import BaseUser
from accounts.utils import CreatedUser, PostProcessingDirector


class UserCreateMixin:
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        try:
            with transaction.atomic():
                baseuser = BaseUser.objects.create_user(**user_data)
                user = self.Meta.model.objects.create(user=baseuser, **validated_data)

                created_user = CreatedUser(user=user, baseuser=baseuser)
                director = PostProcessingDirector(created_user=created_user)
                director.construct_builder()

        except Exception:
            raise
        return user
