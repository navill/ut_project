# from django.contrib import admin
#
# # Register your models here.
# from hospitals.models import MedicalCenter, Department, Major
#
#
# class MedicalCenterAdmin(admin.ModelAdmin):
#     fields = ['country', 'city', 'name', 'address', 'postal_code', 'main_call', 'sub_call']
#     list_display = ['country', 'name', 'address', 'main_call']
#
#
# class DepartmentAdmin(admin.ModelAdmin):
#     fields = ['medical_center', 'name', 'call']
#     list_display = ['medical_center', 'name']
#
#
# class MajorAdmin(admin.ModelAdmin):
#     fields = ['department', 'name', 'call']
#     list_display = ['department', 'name']
#
#
# admin.site.register(MedicalCenter, MedicalCenterAdmin)
# admin.site.register(Department, DepartmentAdmin)
# admin.site.register(Major, MajorAdmin)
