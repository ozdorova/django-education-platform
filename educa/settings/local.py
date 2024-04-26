from .base import *
# export DJANGO_SETTINGS_MODULE=educa.settings.local


DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
