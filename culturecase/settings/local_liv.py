from .base import *  # noqa

ALLOWED_HOSTS = ['culturecase.kdl.kcl.ac.uk']

INTERNAL_IPS = INTERNAL_IPS + ['']

DATABASES = {
    'default': {
        'ENGINE': db_engine,
        'NAME': 'app_culturecase_liv',
        'USER': 'app_culturecase',
        'PASSWORD': '',
        'HOST': ''
    },
}

SECRET_KEY = ''
