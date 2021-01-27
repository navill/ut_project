import random
from celery import shared_task

# beat
from django.contrib.auth import get_user_model

from app_1.models import CeleryTestModel
from config.celery_settings.celery import app

User = get_user_model()


@shared_task(name="sum_two_numbers")
def add(x, y):
    return 0


@shared_task(name="multiply_two_numbers")
def mul(x, y):
    total = x * (y * random.randint(3, 100))
    return total


@shared_task(name="sum_list_numbers")
def xsum(numbers):
    return sum(numbers)


# normal task
@app.task(bind=True)
def test_task(self, value=None, user_id=None):
    user = User.objects.get(id=user_id)
    obj = CeleryTestModel.objects.create(user_id=user.id, host=self.request.hostname)

    # task
    while True:
        value += 1
        if value > 10000:
            result = value
            break
    # self.update_state(state="PROGRESS", meta={'result': result})

    obj.result = result
    obj.is_done = True
    obj.save()
    return result

