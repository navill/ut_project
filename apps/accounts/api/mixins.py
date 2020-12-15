from django.db import transaction

from accounts.models import BaseUser
from accounts.utils import UserAuthenticationHandler


class UserCreateMixin:
    @transaction.atomic
    def create(self, validated_data):
        baseuser = None
        user_data = validated_data.pop('user')
        if self.validate_passwords(user_data):
            baseuser = BaseUser.objects.create_user(**user_data)
        print(self.Meta.model, validated_data)
        user = self.Meta.model.objects.create(user=baseuser, **validated_data)
        print(user)
        user_authentication_handler = UserAuthenticationHandler(user=user, baseuser=baseuser)
        user_authentication_handler.set_group_and_permission()
        return user

    def validate_passwords(self, user_data):
        password = user_data.get('password')
        password2 = user_data.pop('password2')
        if password == password2:
            return True