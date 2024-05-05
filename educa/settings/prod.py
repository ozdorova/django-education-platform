# export DJANGO_SETTINGS_MODULE=educa.settings.prod
import os

from django.conf.global_settings import CSRF_COOKIE_SECURE, SECURE_SSL_REDIRECT, SESSION_COOKIE_SECURE
from .base import *

DEBUG = False

ADMINS = [
    ('Mikhail B.', 'haxboxmiha@gmail.com'),
]

ALLOWED_HOSTS = ['.django-education-platform.ru']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': os.environ.get('POSTGRES_HOST'),
        'PORT': os.environ.get('POSTGRES_PORT'),
    }
}

# for docker
REDIS_URL = 'redis://cache:6379'
CACHES['default']['LOCATION'] = REDIS_URL
CHANNEL_LAYERS['default']['CONFIG']['hosts'] = [REDIS_URL]


# SSL / TLS
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
