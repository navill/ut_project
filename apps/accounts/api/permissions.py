from rest_framework.permissions import BasePermission, IsAuthenticated


class OnlyDoctor(IsAuthenticated):
    def has_permission(self, request, view):  # todo: rest freamework render에서 한번 더 호출되는 문제
        is_auth = super(OnlyDoctor, self).has_permission(request, view)
        is_doc = request.user.groups.filter(name='doctor').exists()
        return bool(is_auth and is_doc)


class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)
