from .base import *  # noqa
import os

# 'localhost:8081'
ALLOWED_HOSTS = os.environ['VIRTUAL_HOST'].split(',')

# INTERNAL_IPS = INTERNAL_IPS + ['137.73.123.143']

DATABASES = {
    'default': {
        'ENGINE': db_engine,
        'NAME': os.environ['POSTGRES_DB'],
        'USER': os.environ['POSTGRES_USER'],
        'PASSWORD': os.environ['POSTGRES_PASSWORD'],
        'HOST': 'db'
    },
}

# DATABASES['default']['HOST'] =
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

# DEBUG=True
WAGTAILSEARCH_BACKENDS['default']['INDEX'] = 'wagtail'

# --------------------------------------------------------------------

ADMINS = ((os.environ['ADMINS_NAME'], os.environ['ADMINS_EMAIL']),)
# SERVER_EMAIL = 'noreply@culturecase.cch.kcl.ac.uk'
SERVER_EMAIL = os.environ['SERVER_EMAIL']
MANAGERS = ADMINS
EMAIL_HOST = os.environ['EMAIL_HOST']

# increase this after successful testing period
if not DEBUG:
    SECURE_HSTS_SECONDS = 3600
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    # SECURE_SSL_REDIRECT = True
