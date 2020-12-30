from rest_framework import permissions


class PermissionMethodBundleMixin:
    def is_safe_method(self, request) -> bool:
        return request.method in permissions.SAFE_METHODS

    def is_superuser(self, request) -> bool:
        return request.user.is_superuser

    def is_authenticated(self, request) -> bool:
        return request.user.is_authenticated

    def is_owner(self, request, obj) -> bool:
        user = request.user
        owner = None
        if hasattr(obj, 'user'):
            owner = obj.user
        elif hasattr(obj, 'writer'):
            owner = obj.writer
        return bool(user == owner)

    # hasattr(self, request.user, 'doctor') vs request.user.groups.filter(name='doctor').exists()
    def has_group(self, request, group_name: str) -> bool:
        return hasattr(request.user, group_name)
