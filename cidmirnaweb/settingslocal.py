from .settingscommon import *

import os

EXTERNAL_BASE_URL = 'http://127.0.0.1:8000'

ANALYSIS_CODE_ROOT = '/home/ale/programming/bio/CID-miRNA'

ANALYSIS_MACHINE = 'localhost'


ADMINS = (
     ('Alejandro Dubrovsky', 'alito@organicrobot.com'),
)

MANAGERS = (
    ('Alejandro Dubrovsky', 'alito@organicrobot.com'),
)


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

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

# Linc2Function 
LINC2FUNCTION_ROOT = '/home/monash/minor_thesis/workspace/linc2functionpipeline/identification'

# SPOT-RNA 
SPOTRNA_ROOT = '/home/monash/minor_thesis/workspace/SPOT-RNA'

# RIblast
RIBLAST_ROOT = '/home/monash/minor_thesis/workspace/RIblast'
RIBLAST_DB = '/home/monash/minor_thesis/workspace/RIblast/mirbase.db/mirbase.db'

