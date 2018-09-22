from .settingscommon import *

import os

EXTERNAL_BASE_URL = 'http://localhost:9000'

ANALYSIS_CODE_ROOT = '/home/ale/programming/bio/CID-miRNA'

ANALYSIS_MACHINE = 'localhost'


ADMINS = (
     ('Alejandro Dubrovsky', 'alito@organicrobot.com'),
)

MANAGERS = (
    ('Alejandro Dubrovsky', 'alito@organicrobot.com'),
    ('Sonika Tyagi', 'sonika.tyagi@gmail.com'),
    ('CID-miRNA', 'cidmirna.help@gmail.com'),
)



EMAIL_HOST = 'localhost'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

STATIC_URL = '/static/'

DELIVERY_ROOT = os.path.join(STATIC_ROOT, DELIVERY_DIRECTORY)
DELIVERY_URL = os.path.join(STATIC_URL, DELIVERY_DIRECTORY)


ALLOWED_HOSTS = ['*']

INTERNAL_IPS = ['127.0.0.1']

MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE

INSTALLED_APPS += [
    'debug_toolbar'
]

# Development database instance
DATABASES = {
    'default': {
        'ENGINE':'django.db.backends.sqlite3', #django.db.backends.', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.path.join(BASE_DIR, 'cidmirna.sqlite')
    }
}

