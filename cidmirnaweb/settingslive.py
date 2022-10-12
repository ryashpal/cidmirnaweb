from .settingscommon import *

import os

ALLOWED_HOSTS = ['bioinformaticslab.erc.monash.edu', '159.65.143.107', '127.0.0.1']

EXTERNAL_BASE_URL = 'http://%s' % ALLOWED_HOSTS[0]

ANALYSIS_CODE_ROOT = '/home/cidmirna/cidmirna'

ANALYSIS_MACHINE = 'localhost'


ADMINS = (
     ('Alejandro Dubrovsky', 'alito@organicrobot.com'),
)

MANAGERS = (
    ('Alejandro Dubrovsky', 'alito@organicrobot.com'),
    ('Sonika Tyagi', 'sonika.tyagi@gmail.com'),
    ('CID-miRNA', 'cidmirna.help@gmail.com'),
)

EMAIL_AVAILABLE = True

EMAIL_HOST = 'localhost'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = True


# Development database instance
DATABASES = {
    'default': {
        'ENGINE':'django.db.backends.sqlite3', #django.db.backends.', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.path.join(BASE_DIR, 'cidmirna.sqlite')
    }
}

# CRC_Finder
DATA_FILE = '/home/cidmirna/cidmirnaweb/crc_finder/predicted_TRAIN_CRCs2_CNN.csv'
DATA_FILE2 = '/home/cidmirna/cidmirnaweb/crc_finder/predicted_VALIDATION_CRCs2_CNN.csv'
DATA_FILE3 = '/home/cidmirna/cidmirnaweb/crc_finder/predicted_TRAIN_CRCs2_RFC.csv'
DATA_FILE4 = '/home/cidmirna/cidmirnaweb/crc_finder/predicted_VALIDATION_CRCs2_RFC.csv'
TEMP_CSV_FILE = './crc_finder/temp_csv_files/'

