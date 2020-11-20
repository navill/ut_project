from django.contrib import admin

# Register your models here.
from accounts.models import BaseUser


class BaseUserAdmin(admin.ModelAdmin):
    fields = ['username', 'email', 'is_active']
    list_display = ['username', 'email', 'last_login', 'date_joined']


admin.site.register(BaseUser, BaseUserAdmin)
