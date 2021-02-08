from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.views.generic import TemplateView


class SignUpView(TemplateView):
    template_name = 'registration/signup.html'

def home(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'doctor'):
            return redirect('accounts:doctor-list')
        else:
            return redirect('accounts:patient-list')
    # return render(request, 'accounts/home.html')


LoginView