import random
from celery import shared_task

# beat
from config.celery_settings.celery import app


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
def test_task(self, x):
    # print('excuted app_1.tasks.py')
    result = {
        'excuted': 'app_1.tasks.py',
        'task_result': x + x,
        'temp': {
            'inner_temp': 1
        }
    }
    self.update_state(state="PROGRESS", meta={'result': result})
    return result
