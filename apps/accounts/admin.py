from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group

from accounts.models import BaseUser, Doctor, Patient


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


class GroupsAdmin(GroupAdmin):
    list_display = ["name", "pk"]


def full_name(obj):
    return obj.user.full_name


class DoctorAdmin(admin.ModelAdmin):
    fields = ['user', full_name, 'major', 'description']
    readonly_fields = ('user', full_name,)
    list_display = ['user', 'major']


class PatientAdmin(admin.ModelAdmin):
    fields = ['user', 'user_doctor', 'age', 'emergency_call']
    readonly_fields = ('user', full_name,)
    list_display = ['user', 'user_doctor', full_name]


admin.site.register(BaseUser, BaseUserAdmin)
admin.site.unregister(Group)
admin.site.register(Group, GroupsAdmin)
admin.site.register(Doctor, DoctorAdmin)
admin.site.register(Patient, PatientAdmin)
