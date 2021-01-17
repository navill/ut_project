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
    # 'default': {
    #     'ENGINE': 'django.db.backends.mysql',
    #     'NAME': 'django_mysql',
    #     'USER': 'root',
    #     'PASSWORD': 'test1234',
    #     'HOST': '127.0.0.1',
    #     'PORT': '3306',
    #     'OPTIONS': {
    #         # 'charset': 'utf8mb4',
    #         # 'use_unicode': True,
    #         # 'init_command': 'SET '
    #         #                 'storage_engine=INNODB,'
    #         #                 'character_set_connection=utf8mb4,'
    #         #                 'collation_connection=utf8mb4_general_ci'
    #         'read_default_file': 'django_mysql.cnf',
    #     },
    #     'TEST_CHARSET': 'utf8mb4',
    #     'TEST_COLLATION': 'utf8mb4_general_ci',
    #     'TEST': {
    #         'CHARSET': 'utf8mb4',
    #         'COLLATION': 'utf8mb4_general_ci',
    #     }
    # }
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': DB_CONF_PATH,
        },
        'TEST': {
            'CHARSET': 'utf8mb4',
            'COLLATION': 'utf8mb4_general_ci'
        }
    }
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
