from django import forms
from django.contrib.auth.forms import UserCreationForm

from accounts.mixins.form_mixins import UserSaveForm
from .models import BaseUser, StaffUser, NormalUser


class StaffSignUpForm(UserSaveForm, UserCreationForm):
    department = forms.CharField(max_length=100)

    class Meta(UserCreationForm.Meta):
        model = BaseUser


class StaffUpdateForm(forms.ModelForm):
    class Meta:
        model = StaffUser
        fields = '__all__'
        # exclude = ['user']


class NormalSignUpForm(UserSaveForm, UserCreationForm):
    description = forms.CharField(max_length=100)

    class Meta(UserCreationForm.Meta):
        model = BaseUser


class NormalUpdateForm(forms.ModelForm):
    class Meta:
        model = NormalUser
        fields = ['user', 'description']
        # exclude = ['user']
