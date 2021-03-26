from django.http import HttpResponse
from django.views.generic.base import View

from app_1.tasks import test_task


# celery view for test
class CeleryTestView(View):
    def get(self, request, *args, **kwargs):
        user_id = self.request.user.id

        # start task
        test_task.delay(value=10000, user_id=user_id)

        return HttpResponse('done')
