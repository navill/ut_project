from django.contrib.auth import login
from django.forms import model_to_dict
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, DetailView, DeleteView, UpdateView
from django.views.generic.base import View

from accounts.forms import DoctorSignUpForm, PatientSignUpForm, DoctorUpdateForm, PatientUpdateForm
from accounts.mixins.view_mixins import OwnerRequiredMixin, UserRequiredMixin, DoctorRequiredMixin

from accounts.models import Doctor, Patient
from app_1.tasks import test_task


class DoctorSignUpView(CreateView):
    form_class = DoctorSignUpForm
    template_name = 'registration/signup_form.html'
    success_url = reverse_lazy('accounts:doctor:list')

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'Doctor'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        obj = form.save()
        login(self.request, obj)
        return redirect(self.success_url)


class DoctorListView(DoctorRequiredMixin, ListView):
    model = Doctor
    template_name = 'user_list.html'
    user_type = 'doctor'

    def get_queryset(self):
        queryset = super().get_queryset().ordered()
        return queryset


class DoctorDetailView(DoctorRequiredMixin, OwnerRequiredMixin, DetailView):
    model = Doctor
    template_name = 'user_detail.html'

    def get_context_data(self, **kwargs):
        kwargs['user_fields'] = model_to_dict(self.object)
        print(self.object)
        # kwargs['patient_list'] = self.object.filter()
        return super().get_context_data(**kwargs)


class DoctorUpdateView(DoctorRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Doctor
    form_class = DoctorUpdateForm
    template_name = 'user_update.html'

    def get_success_url(self):
        return reverse('accounts:doctor:detail', kwargs={'pk': self.object.pk})


class DoctorDeleteView(DoctorRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Doctor
    template_name = 'user_delete.html'

    def get_success_url(self):
        return reverse('accounts:doctor:list')


class PatientSignUpView(CreateView):
    form_class = PatientSignUpForm
    template_name = 'registration/signup_form.html'
    success_url = reverse_lazy('accounts:patient:list')

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'patient'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        obj = form.save()
        login(self.request, obj)
        return redirect(self.success_url)


class PatientListView(UserRequiredMixin, ListView):
    model = Patient
    template_name = 'user_list.html'
    user_type = 'patient'

    def get_queryset(self):
        queryset = super().get_queryset().ordered()
        return queryset


class PatientDetailView(UserRequiredMixin, OwnerRequiredMixin, DetailView):
    model = Patient
    template_name = 'user_detail.html'

    def get_context_data(self, **kwargs):
        kwargs['user_fields'] = model_to_dict(self.object)
        return super().get_context_data(**kwargs)


class PatientUpdateView(UserRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Patient
    form_class = PatientUpdateForm
    template_name = 'user_update.html'

    def get_success_url(self):
        return reverse('accounts:patient:detail', kwargs={'pk': self.object.pk})


class PatientDeleteView(UserRequiredMixin, OwnerRequiredMixin, DeleteView):
    template_name = 'user_delete.html'
    success_url = reverse_lazy('accounts:patient:list')


# celery view for test
class CeleryTestView(View):
    def get(self, request, *args, **kwargs):
        user_id = self.request.user.id

        # start task
        test_task.delay(value=10000, user_id=user_id)

        return HttpResponse('done')
