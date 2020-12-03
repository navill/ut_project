from django.contrib.auth import login
from django.forms import model_to_dict
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, DetailView, DeleteView, UpdateView
from django.views.generic.base import View

from accounts.forms import StaffSignUpForm, NormalSignUpForm, StaffUpdateForm, NormalUpdateForm
from accounts.mixins.view_mixins import StaffRequiredMixin, NormalRequiredMixin, OwnerRequiredMixin
from accounts.models import BaseUser, NormalUser, StaffUser
from app_1.tasks import test_task


class StaffSignUpView(CreateView):
    form_class = StaffSignUpForm
    template_name = 'registration/signup_form.html'
    success_url = reverse_lazy('accounts:staff:list')

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
    user_type = 'staff'

    def get_context_data(self, **kwargs):
        staff_user = self.request.user.staffuser
        kwargs['user_type'] = self.user_type
        kwargs['url'] = staff_user.get_absolute_url()
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        queryset = super().get_queryset().ordered()
        return queryset


class StaffDetailView(StaffRequiredMixin, OwnerRequiredMixin, DetailView):
    model = StaffUser
    template_name = 'user_detail.html'

    def get_context_data(self, **kwargs):
        kwargs['user_fields'] = model_to_dict(self.object)
        return super().get_context_data(**kwargs)


class StaffUpdateView(StaffRequiredMixin, OwnerRequiredMixin, UpdateView):
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
    user_type = 'normal'

    def get_context_data(self, **kwargs):
        normal_user = self.request.user.normaluser
        kwargs['user_type'] = self.user_type
        kwargs['url'] = normal_user.get_absolute_url()
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        queryset = super().get_queryset().ordered()
        return queryset

    def dispatch(self, request, *args, **kwargs):
        kwargs['user_type'] = self.user_type
        return super().dispatch(request, *args, **kwargs)


class NormalDetailView(NormalRequiredMixin, OwnerRequiredMixin, DetailView):
    model = NormalUser
    template_name = 'user_detail.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'Normal'
        kwargs['user_fields'] = model_to_dict(self.object)
        return super().get_context_data(**kwargs)


class NormalUpdateView(NormalRequiredMixin, OwnerRequiredMixin, UpdateView):
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


# celery view for test
class CeleryTestView(View):
    def get(self, request, *args, **kwargs):
        user_id = self.request.user.id

        # start task
        test_task.delay(value=10000, user_id=user_id)

        return HttpResponse('done')
