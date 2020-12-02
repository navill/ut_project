# 201202

### Celery Settings

```python
# config.celery_settings.celery.py
from __future__ import absolute_import, unicode_literals

import os
from datetime import timedelta

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

BASE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6001')
app = Celery('celery_settings')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# celery - config
app.conf.broker_url = BASE_REDIS_URL
# app.conf.accept_content = ['json']
app.conf.result_backend = 'db+sqlite:///config/celery_settings/results/results.sqlite'
app.conf.result_extended = True
app.conf.beat_scheduler = 'django_celery_beat.schedulers.DatabaseScheduler'

app.conf.beat_schedule = {
    'add-every-minute-crontab': {
        'task': 'multiply_two_numbers',
        'schedule': crontab(hour=1, minute=3),
        'args': (16, 16)
    },
    'add-every-5-seconds': {
        'task': 'multiply_two_numbers',
        'schedule': timedelta(seconds=5),
        'args': (16, 16)
    },
    'add-every-30-seconds': {
        'task': 'sum_two_numbers',
        'schedule': timedelta(seconds=30),
        'args': (16, 16)
    },
}

```

<br>

```python
# config.settings.local
import redis
import djcelery

from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

# debug toolbar
INSTALLED_APPS += [
    'debug_toolbar',
    'djcelery',
    'django_celery_beat',
    'django_celery_results',
]

MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
INTERNAL_IPS = [
    '127.0.0.1',
]

# database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# celery for local setting
djcelery.setup_loader()

# redis for local setting
REDIS_HOST = 'localhost'
REDIS_PORT = 6001  
REDIS_DB = 1
REDIS_CONN_POOL_1 = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=1, decode_responses=True)
```

<br>

-   redis는 docker를 이용해 설정됨(6001:6000)

![image-20201202114752572](/Users/jh/Desktop/ut_django/docs/image-20201202114752572.png)

```python
# external terminal(mac)
$ docker start redis_test
$ docker attach redis_test

# internal terminal(docker)
$ redis-server --port 6000 --daemonize yes  # background mode
$ redis-cli -p 6000 shutdown  # 종료
```

<br>

### Celery Task

```python
# apps.app_1.tasks.py
import random
from celery import shared_task

from config.celery_settings.celery import app

# scheduling task
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


# normal async task
@app.task(bind=True)
def test_task(self, x):
    # print('excuted app_1.tasks.py')
    result = {
        'excuted': 'app_1.tasks.py',
        'task_result': x + x,
        'host': self.request.hostname,
        'temp': {
            'inner_temp': 1
        }
    }
    self.update_state(state="PROGRESS", meta={'result': result})
    return result

  
# output
[2020-12-02 12:52:45,802: INFO/ForkPoolWorker-8] Task app_1.tasks.test_task[53754495-8ed5-45f5-95c0-e7ba3d9e445d] succeeded in 0.04503535100000011s: {
  'excuted': 'app_1.tasks.py', 
  'task_result': 200, 
  'host': 'celery@apples-MacBook-Pro.local', 
  'temp': {'inner_temp': 1}
}
```

**bind**: task 데코레이터의 bind 인자는 task 인스턴스(self)에 접근 가능토록 한다.

[Celery task option](https://docs.celeryproject.org/en/stable/userguide/tasks.html?highlight=bind#general)

