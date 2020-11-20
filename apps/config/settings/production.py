from .base import *

DEBUG = False
ALLOWED_HOSTS = ['http://127.0.0.1:8000']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
