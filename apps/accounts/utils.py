from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q


class UserAuthenticationHandler:
    def __init__(self, user=None, baseuser=None):
        self.user = user
        self.baseuser = baseuser
        self.role = None
        self.permissions = None

    def set_group_and_permission(self):
        self.set_role(self.user)
        self.set_permissions()
        self.set_group_as_role()
        self.set_permission_to_baseuser()

    def set_permissions(self):
        model_query = Q(model=self.role)  # role user model permission
        content_type_query = Q()

        if self.role == 'doctor':
            model_query |= Q(model='prescription')  # prescription model permission

        content_types = ContentType.objects.filter(model_query, app_label='accounts')
        if content_types.count() > 1:
            for content in content_types:
                content_type_query |= Q(content_type=content)
        else:
            content_type_query = Q(content_type=content_types.first())

        self.permissions = Permission.objects.filter(content_type_query)

    def set_group_as_role(self):
        group, created = Group.objects.get_or_create(name=self.role)
        if created:
            group.permissions.set(self.permissions)
        self.baseuser.groups.add(group)

    def set_permission_to_baseuser(self):
        self.baseuser.user_permissions.set(self.permissions)

    def set_role(self, user):
        self.role = user.__class__.__name__.lower()
