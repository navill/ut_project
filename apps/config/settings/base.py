import json
import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ROOT_DIR = BASE_DIR.parent

KEY_PATH = os.path.join(ROOT_DIR, 'secrets.json')
DB_CONF_PATH = os.path.join(BASE_DIR, 'django_mysql.cnf')
DB_TEST_CONF_PATH = os.path.join(BASE_DIR, 'django_mysql_test.cnf')
with open(KEY_PATH) as f:
    secrets = json.loads(f.read())


def get_secret(setting, secrets=secrets):
    try:
        return secrets[setting]
    except KeyError:
        error_msg = f'Set the {setting} environment variable'
        raise ImproperlyConfigured(error_msg)


SECRET_KEY = get_secret("SECRET_KEY")

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # apps
    'accounts',
    'hospitals',
    'prescriptions',
    'core',
    'files',
    # third party
    'rest_framework',
    'crispy_forms',
    'rest_framework_simplejwt.token_blacklist',
    'django_filters',
    'djcelery',
    'django_celery_beat',
    'django_celery_results',
    'drf_yasg',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = False

DATETIME_INPUT_FORMAT = ['%Y-%m-%dT%H:%M:%S']
DATE_INPUT_FORMAT = ['%Y-%m-%d']

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'
CRISPY_TEMPLATE_PACK = 'bootstrap4'

AUTH_USER_MODEL = 'accounts.BaseUser'

LOGIN_URL = 'login'
LOGOUT_URL = 'logout'

REST_FRAMEWORK = {
    # 'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_FILTER_BACKENDS': ['config.utils.filter_backends.CustomDjangoFilterBackend'],

    'DEFAULT_PERMISSION_CLASSES': [
        'accounts.api.permissions.IsSuperUser',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # 'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'accounts.api.authentications.CustomBaseAuthentication',
        'accounts.api.authentications.CustomJWTTokenUserAuthentication',
    ],
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'DEFAULT_PAGINATION_CLASS': 'config.utils.pagination_backends.FasterPagination',
    'PAGE_SIZE': 30
}

SWAGGER_SETTINGS = {
    'DEFAULT_AUTO_SCHEMA_CLASS': 'config.utils.doc_utils.CustomAutoSchema',
    'DEFAULT_GENERATOR_CLASS': 'config.utils.doc_utils.CustomOpenAPISchemaGenerator',
}

# https://github.com/nextghost/sciswarm/blob/e835c2e1ed331a1e436214c7fbd82849b3c37f52/sciswarm/settings_private_example.py
# logging 샘플 코드
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'formatters': {
#         'simple': {
#             'format': '%(asctime)s %(levelname)s %(message)s'
#         }
#     },
#     'handlers': {
#         'sciswarm_file': {
#             'level': 'DEBUG',
#             'class': 'logging.FileHandler',
#             'filename': '/var/log/django/sciswarm.log',
#             'formatter': 'simple',
#         },
#         'stderr': {
#             'level': 'DEBUG',
#             'class': 'logging.StreamHandler',
#             'formatter': 'simple',
#         },
#     },
#     'loggers': {
#         'sciswarm': {
#             'handlers': ['sciswarm_file'],
#             'level': 'DEBUG',
#             'propagate': True,
#         },
#         'sciswarm.harvest': {
#             'handlers': ['stderr'],
#             'level': 'DEBUG',
#             'propagate': False,
#         },
#     },
# }
