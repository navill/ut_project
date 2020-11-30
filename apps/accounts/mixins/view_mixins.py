from django.contrib.auth.mixins import AccessMixin


class NormalRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not (user.is_authenticated and user.is_normal):  # todo: DRY 적용
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class StaffRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not (user.is_authenticated and user.is_staff):
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


def get_role_from_model():
    pass
