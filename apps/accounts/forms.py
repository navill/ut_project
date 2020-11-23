from django import forms
from django.contrib.auth.forms import UserCreationForm

from .mixins import UserSaveForm
from .models import BaseUser


class StaffSignUpForm(UserSaveForm, UserCreationForm):
    department = forms.CharField(max_length=100)

    class Meta(UserCreationForm.Meta):
        model = BaseUser


class NormalSignUpForm(UserSaveForm, UserCreationForm):
    description = forms.CharField(max_length=100)

    class Meta(UserCreationForm.Meta):
        model = BaseUser
