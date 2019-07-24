"""
Django settings for CommunicationSeminar project.

Generated by 'django-admin startproject' using Django 1.11.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import sys
import urllib.parse


def env_get(name, default=None):
    return os.environ.get(name, default)

def env_get_int(name, default=None):
    return int(env_get(name, default))

def env_get_bool(name, default=None):
    return bool(env_get_int(name, default))


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env_get('SECRET_KEY', "c7so+hqfe+a_9i9*##vgl!k-xb^)nin&o-ev*^t@ipq6y!wt!-")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env_get_bool("DEBUG", True)
LIVE = env_get_bool("LIVE", False)

ZEKES_EMAIL = 'zekehuntergreen@gmail.com'
JAMES_EMAIL = 'hunter@gonzaga.edu'
ADMINS = [('Zeke Hunter-Green', ZEKES_EMAIL)]
CONTACT_FORM_RECIPIENTS = [ZEKES_EMAIL, JAMES_EMAIL]

ALLOWED_HOSTS = [
    'comsem.herokuapp.com',
    'localhost',
    '.comsem.net',
]

# Application definition

INSTALLED_APPS = [
    'ComSemApp.apps.ComsemappConfig',
    'error_recognition.apps.ErrorRecognitionConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'storages',
    'django_select2',
    'django_extensions',
]

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'CommunicationSeminar.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                "ComSemApp.context_processors.user_info",
            ],
        },
    },
]

WSGI_APPLICATION = 'CommunicationSeminar.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {}

if LIVE:
    # Register database schemes in URLs.
    urllib.parse.uses_netloc.append('mysql')

    try:

        # Check to make sure DATABASES is set in settings.py file.
        # If not default to {}

        if 'DATABASES' not in locals():
            DATABASES = {}

        if 'CLEARDB_DATABASE_URL' in os.environ:
            url = urllib.parse.urlparse(os.environ['CLEARDB_DATABASE_URL'])

            # Ensure default database exists.
            DATABASES['default'] = DATABASES.get('default', {})

            # Update with environment configuration.
            DATABASES['default'].update({
                'NAME': url.path[1:],
                'USER': url.username,
                'PASSWORD': url.password,
                'HOST': url.hostname,
                'PORT': url.port,
            })

            if url.scheme == 'mysql':
                DATABASES['default']['ENGINE'] = 'django.db.backends.mysql'
    except Exception:
        print('Unexpected error:', sys.exc_info())
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'HOST': 'localhost',
            'PORT': '3306',
            'NAME': 'CommunicationSeminarDjango',
            'USER': 'root',
            'PASSWORD': '2017%ComSem',
        }
    }



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


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# where should the login form redirect to?
LOGIN_REDIRECT_URL = '/initiate_roles/'

# EMAIL
if LIVE:
    EMAIL_HOST = env_get('EMAIL_HOST', 'smtp.sendgrid.net')
    EMAIL_PORT = env_get('EMAIL_PORT', 587)
    EMAIL_HOST_USER = env_get('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = env_get('EMAIL_HOST_PASSWORD')
    EMAIL_USE_TLS = env_get('EMAIL_USE_TLS', True)
    DEFAULT_FROM_EMAIL = env_get('DEFAULT_FROM_EMAIL', 'ComSem <noreply@comsem.net>')
else:
    EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
    EMAIL_FILE_PATH = 'app-messages'

# HTTPS
if LIVE:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'loggers': {
        # Silence SuspiciousOperation.DisallowedHost exception ('Invalid
        # HTTP_HOST' header messages). Set the handler to 'null' so we don't
        # get those annoying emails.
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'level': 'CRITICAL',
            'propagate': False,
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
STATIC_ROOT  =   os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

#  Add configuration for static files storage using whitenoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Media
MEDIA_ROOT = os.path.join(BASE_DIR, 'efs')
MEDIA_URL = '/efs/'

if LIVE:
    SECURE_SSL_REDIRECT = True

# Amazon S3
if LIVE:
    AWS_ACCESS_KEY_ID = env_get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = env_get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = env_get('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }

    DEFAULT_FILE_STORAGE = 'CommunicationSeminar.storage_backends.MediaStorage'
