from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction

from .mixins import UserFormMixin
from .models import BaseUser


class StaffSignUpForm(UserFormMixin, UserCreationForm):
    department = forms.CharField(max_length=100)

    class Meta(UserCreationForm.Meta):
        model = BaseUser

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user = self.set_role(user)
        user.save()
        self.create_user_with_groups(user=user)
        return user

    def set_role(self, user: BaseUser = None) -> BaseUser:
        user.is_staff = True
        user.is_normal = False
        return user


class NormalSignUpForm(UserFormMixin, UserCreationForm):
    description = forms.CharField(max_length=100)

    class Meta(UserCreationForm.Meta):
        model = BaseUser

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user = self.set_role(user)
        user.save()
        self.create_user_with_groups(user=user)
        return user

    def set_role(self, user: BaseUser = None) -> BaseUser:
        user.is_staff = False
        user.is_normal = True
        return user
