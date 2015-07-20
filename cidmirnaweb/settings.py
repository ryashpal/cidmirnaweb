"""
Django settings for cidmirnaweb project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))

EXTERNAL_BASE_URL = 'http://melb.agrf.org.au:8888'
INTERNAL_BASE_URL = 'http://biowebs.agrf.org.au'

# How many analyses we let run at the same time
MAX_SIMULTANEOUS_ANALYSIS = 1 

DELIVERY_DIRECTORY = 'delivery'

ANALYSIS_CODE_ROOT = '/home/dubrova/src/CID-miRNA'

# Where to stick the uploaded data
UPLOAD_DIRECTORY = os.path.join(BASE_DIR, 'uploaded')

ANALYSIS_MACHINE = 'blade_dev03'

ADMINS = (
     ('Alejandro Dubrovsky', 'alex.dubrovsky@agrf.org.au'),
)

MANAGERS = (
    ('Alejandro Dubrovsky', 'alex.dubrovsky@agrf.org.au'),
    ('Sonika Tyagi', 'sonika.tyagi@agrf.org.au'),
    ('CID-miRNA', 'cidmirna.help@gmail.com'),
)

EMAIL_HOST = 'exchmelb01.agrf.org.au'

# Development database instance
DATABASES = {
    'default': {
        'ENGINE':'django.db.backends.sqlite3', #django.db.backends.', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.path.join(BASE_DIR, 'cidmirna.sqlite')
    }
}


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'v%iyy@@@xy6jyq&@$k#+5!ktcrhi2k@4219ia01g4k8jg94u_a'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['biowebs.agrf.org.au', 'melb.agrf.org.au']


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'analyses',
    'django_static',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)


# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)


TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    "/home/dubrova/public_html/cidmirnaweb/templates/",
)


STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'otherstatic'),
)

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = '/home/dubrova/public_html/cidmirnaweb/static/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/cidmirna/static/'

DELIVERY_ROOT = os.path.join(STATIC_ROOT, DELIVERY_DIRECTORY)
DELIVERY_URL = os.path.join(STATIC_URL, DELIVERY_DIRECTORY)

DJANGO_STATIC_MEDIA_ROOTS = [STATIC_ROOT]
DJANGO_STATIC_SAVE_PREFIX = os.path.join(STATIC_ROOT, 'django_static_links')
DJANGO_STATIC_NAME_PREFIX = '/cidmirna/static/django_static_links'

CRISPY_TEMPLATE_PACK = 'bootstrap3'

ROOT_URLCONF = 'cidmirnaweb.urls'

WSGI_APPLICATION = 'cidmirnaweb.wsgi.application'


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/cidmirna/static/'

DJANGO_STATIC = True


import datetime
import logging

class NoDBFilter(logging.Filter):
    """
    Let through anything that's not emitted by django.db.backends
    """
    def filter(self, record):
        return record.name != 'django.db.backends'

class NoParamikoFilter(logging.Filter):
    """
    Let through anything that's not emitted by paramiko
    """
    def filter(self, record):
        return not record.name.startswith('paramiko')


logDirectory = os.path.join(BASE_DIR, 'logs')
logPath = os.path.join(logDirectory,'log-%s.txt' % datetime.datetime.now().strftime('%Y%m%d'))
logNodbPath = os.path.join(logDirectory,'lognodb-%s.txt' % datetime.datetime.now().strftime('%Y%m%d'))


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters' : [],  # Filter out paramiko since it adds too much noise
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html' : True
        },
    },
    'loggers' : {},
    'filters' : {
    }
}


if 'formatters' not in LOGGING:
    LOGGING['formatters'] = {}

LOGGING['formatters']['verbose'] = {
    'format': '%(levelname)s|%(asctime)s|%(name)s|%(message)s'
}

if 'filters' not in LOGGING:
    LOGGING['filters'] = {}


LOGGING['filters']['nodb'] = {
    '()' : NoDBFilter
}

LOGGING['handlers']['file'] = {
        'level' : 'DEBUG',
        'filters' : [],
        'class' : 'logging.FileHandler',
        'formatter' : 'verbose',
        'delay' : True,
        'filename' : logPath
    }

LOGGING['handlers']['nosql'] = {
        'level' : 'DEBUG',
        'filters' : ['nodb'],
        'class' : 'logging.FileHandler',
        'formatter' : 'verbose',
        'delay' : True,
        'filename' : logNodbPath
    }


LOGGING['loggers'][''] = {
        'handlers' : ['file', 'nosql','mail_admins'],
        'level' : 'DEBUG',
        'propagate' : True
    }

del datetime, logPath, logNodbPath, logDirectory


