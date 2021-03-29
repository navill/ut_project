from config.settings.local import *


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': DB_TEST_CONF_PATH,
        },
    },
}
