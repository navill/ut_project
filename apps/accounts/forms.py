from django import forms
from django.contrib.auth.forms import UserCreationForm

from accounts.mixins.form_mixins import UserSaveMixin
from .models import BaseUser, Doctor, Patient


class DoctorSignUpForm(UserSaveMixin, UserCreationForm):
    department = forms.CharField(max_length=100)

    class Meta(UserCreationForm.Meta):
        model = BaseUser


class DoctorUpdateForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['department']


class PatientSignUpForm(UserSaveMixin, UserCreationForm):
    description = forms.CharField(max_length=100)

    class Meta(UserCreationForm.Meta):
        model = BaseUser


class PatientUpdateForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['prescription']
