import redis

from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

# debug toolbar
INSTALLED_APPS += [
    'debug_toolbar',
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

# celery


# redis
REDIS_HOST = 'localhost'
REDIS_PORT = 6001
REDIS_DB = 1
REDIS_CONN_POOL_1 = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=1, decode_responses=True)
