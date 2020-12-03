from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied


class NormalRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not (user.is_authenticated and user.normaluser.is_normal):  # todo: DRY 적용
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class StaffRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not (user.is_authenticated and user.staffuser.is_staff):  # todo: DRY 적용
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class OwnerRequiredMixin:
    def get_object(self, queryset=None):
        obj = super().get_object()
        if self.request.user.username == obj.user.username:
            return obj
        raise PermissionDenied('Forbidden')
