from datetime import timedelta

import redis
import djcelery

from .base import *

DEBUG = True

if DEBUG:
    # debug toolbar
    INSTALLED_APPS += [
        'debug_toolbar',
    ]

    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    INTERNAL_IPS = [
        '127.0.0.1',
    ]

ALLOWED_HOSTS = ['*']

# database
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': DB_CONF_PATH,
        },
    },
}

# celery for local setting
djcelery.setup_loader()

# redis for local setting
REDIS_HOST = 'localhost'
REDIS_PORT = 6001
REDIS_DB = 1
REDIS_CONN_POOL_1 = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=1, decode_responses=True)

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,

    # 'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': (
        'rest_framework_simplejwt.tokens.AccessToken',
        # 'rest_framework_simplejwt.tokens.SlidingToken'
    ),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(days=1),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

MEDIA_URL = '/storage/'
MEDIA_ROOT = os.path.join(BASE_DIR, "storage")
