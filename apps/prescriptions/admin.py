# from django.contrib import admin
#
# from prescriptions.models import Prescription, FilePrescription
#
#
# class FilePrescriptionInLine(admin.TabularInline):
#     model = FilePrescription
#     fields = ['description', 'status', 'checked', 'day_number', 'date', 'active', 'uploaded']
#     readonly_fields = ['description', 'day_number', 'date', 'status', 'checked', 'active', 'uploaded']
#
#
# class PrescriptionAdmin(admin.ModelAdmin):
#     fields = ['writer', 'patient', 'description', 'start_date', 'end_date', 'status', 'checked', 'created_at',
#               'updated_at', 'deleted']
#     readonly_fields = ['writer', 'patient', 'created_at', 'updated_at']
#     list_display = ['id', 'writer_name', 'patient_name', 'start_date', 'end_date', 'status', 'checked', 'deleted',
#                     'created_at', 'updated_at']
#     list_filter = ['writer', 'patient', 'status', 'checked', 'created_at', 'updated_at']
#     search_fields = ['writer']
#
#     inlines = [FilePrescriptionInLine]
#     list_per_page = 100
#
#     def get_queryset(self, request):
#         queryset = super().get_queryset(request)
#         return queryset
#
#     def writer_name(self, obj):
#         return obj.writer_name
#
#     def patient_name(self, obj):
#         return obj.patient_name
#
#
# admin.site.register(Prescription, PrescriptionAdmin)
