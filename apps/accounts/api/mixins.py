from django.db import transaction

from accounts.models import BaseUser


class UserCreateMixin:
    @transaction.atomic
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        base_user = BaseUser.objects.create_user(**user_data)
        obj = self.Meta.model.objects.create(user=base_user, **validated_data)
        return obj