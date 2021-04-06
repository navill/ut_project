from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied


class UserRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class DoctorRequiredMixin(UserRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        request_handler = super().dispatch(request, *args, **kwargs)
        if self.request.user.user_type.doctor:
            return request_handler
        else:
            return self.handle_no_permission()


class OwnerRequiredMixin:
    def get_object(self, queryset=None):
        try:
            obj = super().get_object()
            if self.request.user.email == obj.user.email:
                return obj
        except Exception:
            raise PermissionDenied('Forbidden')
