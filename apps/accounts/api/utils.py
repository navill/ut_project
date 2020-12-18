from rest_framework import permissions


def is_safe_method(request) -> bool:
    return request.method in permissions.SAFE_METHODS


def is_superuser(request) -> bool:
    return request.user.is_superuser


def is_authenticated(request) -> bool:
    return request.user.is_authenticated


def is_owner(request, obj) -> bool:
    user = request.user
    owner = None
    if hasattr(obj, 'user'):
        owner = obj.user
    elif hasattr(obj, 'writer'):
        owner = obj.writer
    return bool(user == owner)


# hasattr(request.user, 'doctor') vs request.user.groups.filter(name='doctor').exists()
def has_group(request, group_name: str) -> bool:
    return hasattr(request.user, group_name)


# def get_type_user(request, group_name) -> Any[User, None]:
#     return getattr(request.user, group_name, None)


def check_view(view, target):
    view_name = view.__class__.__name__
    return True if target in view_name else False
