from __future__ import absolute_import, unicode_literals

import os
from datetime import timedelta

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

BASE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6001')
app = Celery('celery_settings')
print(BASE_REDIS_URL)
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.broker_url = BASE_REDIS_URL
app.conf.accept_content = ['json']
app.conf.result_backend = 'db+sqlite:///config/celery_settings/results/results.sqlite'
app.conf.result_extended = True
app.conf.beat_scheduler = 'django_celery_beat.schedulers.DatabaseScheduler'
app.conf.beat_schedule = {
    'add-every-minute-crontab': {
        'task': 'multiply_two_numbers',
        'schedule': crontab(hour=1, minute=3),
        'args': (16, 16),
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
