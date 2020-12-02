import json

from django.contrib.auth import login
from django.forms import model_to_dict
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, DetailView, DeleteView, UpdateView
from django.views.generic.base import View
from rest_framework.views import APIView

from accounts.forms import StaffSignUpForm, NormalSignUpForm, StaffUpdateForm, NormalUpdateForm
from accounts.mixins.view_mixins import StaffRequiredMixin, NormalRequiredMixin
from accounts.models import BaseUser, NormalUser, StaffUser
from app_1.tasks import test_task


class StaffSignUpView(CreateView):
    model = BaseUser
    form_class = StaffSignUpForm
    template_name = 'registration/signup_form.html'

    # success_url = reverse_lazy('accounts:staff:list')

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'Staff'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        saved_user = form.save()
        login(self.request, saved_user)
        return redirect('accounts:staff:list')


class StaffListView(StaffRequiredMixin, ListView):
    model = StaffUser
    template_name = 'user_list.html'
    success_url = reverse_lazy('accounts:normal:list')

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'Staff User'
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        queryset = super().get_queryset().ordered()
        return queryset


class StaffDetailView(StaffRequiredMixin, DetailView):
    model = StaffUser
    template_name = 'user_detail.html'


class StaffUpdateView(StaffRequiredMixin, UpdateView):
    model = StaffUser
    form_class = StaffUpdateForm
    template_name = 'user_update.html'

    def get_success_url(self):
        return reverse('accounts:staff:detail', kwargs={'pk': self.object.pk})


class StaffDeleteView(StaffRequiredMixin, DeleteView):
    model = StaffUser
    template_name = 'user_delete.html'

    def get_success_url(self):
        return reverse('accounts:staff:list')


class NormalSignUpView(CreateView):
    model = NormalUser
    form_class = NormalSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'Normal'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        saved_user = form.save()
        login(self.request, saved_user)
        return redirect('accounts:normal:list')


class NormalListView(NormalRequiredMixin, ListView):
    model = NormalUser
    template_name = 'user_list.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'Normal User'
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        queryset = super().get_queryset().ordered()
        return queryset


class NormalDetailView(NormalRequiredMixin, DetailView):
    model = NormalUser
    template_name = 'user_detail.html'

    def get_object(self, queryset=None):
        obj = super().get_object()
        if self.request.user.username == obj.user.username:
            return obj

    def get_context_data(self, **kwargs):
        kwargs['user_fields'] = model_to_dict(self.object)
        return super().get_context_data(**kwargs)


class NormalUpdateView(NormalRequiredMixin, UpdateView):
    model = NormalUser
    form_class = NormalUpdateForm
    template_name = 'user_update.html'

    def get_success_url(self):
        return reverse('accounts:normal:detail', kwargs={'pk': self.object.pk})


class NormalDeleteView(DeleteView):
    model = NormalUser
    template_name = 'user_delete.html'

    def get_success_url(self):
        return reverse('accounts:normal:list')


class CeleryTestView(View):
    def get(self, request, *args, **kwargs):
        result = test_task.delay(100)
        response = result.get(propagate=False)
        json_response = json.dumps(response, indent=4)
        return HttpResponse(json_response)
