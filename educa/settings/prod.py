# export DJANGO_SETTINGS_MODULE=educa.settings.prod
from .base import *

DEBUG = False

ADMINS = [
    ('Mikhail B.', 'haxboxmiha@gmail.com'),
]

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {

    }
}
