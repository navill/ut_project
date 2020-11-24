from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, DetailView, DeleteView, UpdateView

from accounts.decorators import staff_required, normal_required
from accounts.forms import StaffSignUpForm, NormalSignUpForm
from accounts.models import BaseUser, NormalUser, StaffUser


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


@method_decorator([login_required, staff_required], name='dispatch')
class StaffListView(ListView):
    model = StaffUser
    template_name = 'user_list.html'
    success_url = reverse_lazy('accounts:normal:list')

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'Staff User'
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        queryset = super().get_queryset().ordered()
        return queryset


class StaffDetailView(DetailView):
    model = StaffUser
    template_name = 'user_detail.html'


class StaffUpdateView(UpdateView):
    model = StaffUser
    template_name = 'user_update.html'

    def get_success_url(self):
        return reverse('accounts:staff:detail', kwargs={'pk': self.object.pk})


class StaffDeleteView(DeleteView):
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


@method_decorator([login_required, normal_required], name='dispatch')
class NormalListView(ListView):
    model = NormalUser
    template_name = 'user_list.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'Normal User'
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        queryset = super().get_queryset().ordered()
        return queryset


class NormalDetailView(DetailView):
    model = NormalUser
    template_name = 'user_detail.html'


class NormalUpdateView(UpdateView):
    model = NormalUser
    template_name = 'user_update.html'

    def get_success_url(self):
        return reverse('accounts:normal:detail', kwargs={'pk': self.object.pk})


class NormalDeleteView(DeleteView):
    model = NormalUser
    template_name = 'user_delete.html'

    def get_success_url(self):
        return reverse('accounts:normal:list')
