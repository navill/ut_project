from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group

from accounts.models import BaseUser


class BaseUserAdmin(admin.ModelAdmin):
    fields = ['username', 'email', 'is_active', 'groups']
    list_display = ['username', 'get_groups', 'email', 'last_login', 'date_joined']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related('groups')
        return queryset

    def get_groups(self, obj):
        if obj.is_superuser:
            groups = list()
            user_groups = obj.groups.filter(user=obj).values_list('name', flat=True)
            for group in user_groups:
                groups.append(group)
            return ', '.join(groups)
        return obj.groups.get(user=obj).name

    get_groups.short_description = "groups"
    # get_groups.admin_order_field = "groups"


admin.site.register(BaseUser, BaseUserAdmin)


class GroupsAdmin(GroupAdmin):
    list_display = ["name", "pk"]


admin.site.unregister(Group)
admin.site.register(Group, GroupsAdmin)
