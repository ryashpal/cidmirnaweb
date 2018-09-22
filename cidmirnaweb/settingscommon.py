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

# How many analyses we let run at the same time
MAX_SIMULTANEOUS_ANALYSIS = 1 

DELIVERY_DIRECTORY = 'delivery'


# Where to stick the uploaded data
UPLOAD_DIRECTORY = os.path.join(BASE_DIR, 'uploaded')


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'v%iyy@@@xy6jyq&@$k#+5!ktcrhi2k@4219ia01g4k8jg94u_a'



# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'analyses',
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

FILE_UPLOAD_PERMISSIONS = 0o664

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


CRISPY_TEMPLATE_PACK = 'bootstrap3'

ROOT_URLCONF = 'cidmirnaweb.urls'

WSGI_APPLICATION = 'cidmirnaweb.wsgi.application'


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-au'

TIME_ZONE = 'Australia/Melbourne'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/


STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'other_static'),
]



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


