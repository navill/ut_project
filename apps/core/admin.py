from django.contrib import admin

# Register your models here.

# admin.site.unregister()
from djcelery.models import TaskState, WorkerState, IntervalSchedule, CrontabSchedule, PeriodicTask
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

admin.site.unregister(TaskState)
admin.site.unregister(WorkerState)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(PeriodicTask)

admin.site.unregister(BlacklistedToken)
admin.site.unregister(OutstandingToken)