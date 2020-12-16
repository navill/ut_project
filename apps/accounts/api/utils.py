from rest_framework import permissions


def is_safe_method(request) -> bool:
    return request.method in permissions.SAFE_METHODS


def is_superuser(request) -> bool:
    return request.user.is_superuser


def is_authenticated(request) -> bool:
    return request.user.is_authenticated


def check_owner(request, obj) -> bool:
    user = request.user
    owner = None
    if hasattr(obj, 'user'):
        owner = obj.user
    elif hasattr(obj, 'writer'):
        owner = obj.writer
    return bool(user == owner)


def has_group(request, group_name: str) -> bool:
    return request.user.groups.filter(name=group_name).exists()
