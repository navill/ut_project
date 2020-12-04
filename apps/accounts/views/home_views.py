from django.shortcuts import redirect, render
from django.views.generic import TemplateView


class SignUpView(TemplateView):
    template_name = 'registration/signup.html'


def home(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'staffuser'):
            return redirect('accounts:staff:list')
        else:
            return redirect('accounts:normal:list')
    return render(request, 'accounts/home.html')
