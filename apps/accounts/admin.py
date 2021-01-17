from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group

from accounts.models import BaseUser, Doctor, Patient


class BaseUserAdmin(admin.ModelAdmin):
    fields = ['email', 'is_active', 'groups']
    list_display = ['get_groups', 'email', 'last_login', 'created_at']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related('groups').prefetch_related('doctor').prefetch_related('patient')
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


# def full_name(obj):
#     return obj.user.get_child_username()


class DoctorAdmin(admin.ModelAdmin):
    fields = ['user', 'first_name', 'last_name', 'major', 'description']
    readonly_fields = ('user', 'first_name', 'last_name',)
    list_display = ['user', 'major']


class PatientAdmin(admin.ModelAdmin):
    fields = ['user', 'doctor', 'age', 'emergency_call']
    readonly_fields = ('user', 'first_name', 'last_name',)
    list_display = ['user', 'doctor', 'first_name', 'last_name']


admin.site.register(BaseUser, BaseUserAdmin)
admin.site.unregister(Group)
admin.site.register(Group, GroupsAdmin)
admin.site.register(Doctor, DoctorAdmin)
admin.site.register(Patient, PatientAdmin)
