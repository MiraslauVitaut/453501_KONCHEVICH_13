import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-realty-agency-lab5-secret-key-2024'

DEBUG = True

import os
_RENDER_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '')
ALLOWED_HOSTS = ['localhost', '127.0.0.1', _RENDER_HOSTNAME] if _RENDER_HOSTNAME else ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',
    'rest_framework',
    'main',
    'properties',
    'users',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'realty_agency.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'realty_agency.wsgi.application'

import os

# Если задана DATABASE_URL (Docker/продакшен) — используем PostgreSQL
# Иначе — SQLite для локальной разработки
_DATABASE_URL = os.environ.get('DATABASE_URL', '')

if _DATABASE_URL:
    import urllib.parse
    _url = urllib.parse.urlparse(_DATABASE_URL)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': _url.path.lstrip('/'),
            'USER': _url.username,
            'PASSWORD': _url.password,
            'HOST': _url.hostname,
            'PORT': _url.port or 5432,
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db' / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Minsk'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise для раздачи статики на Render
MIDDLEWARE_WHITENOISE = 'whitenoise.middleware.WhiteNoiseMiddleware'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.CustomUser'

LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# Logging
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')

# Логирование: на Render/продакшен — только консоль, локально — консоль + файл
import os as _os
_LOGS_DIR = BASE_DIR / 'logs'
_USE_FILE_LOGGING = _os.path.isdir(str(_LOGS_DIR))

_log_handlers = {'console': {'class': 'logging.StreamHandler', 'formatter': 'simple'}}
_handler_list = ['console']

if _USE_FILE_LOGGING:
    _log_handlers['file'] = {
        'class': 'logging.FileHandler',
        'filename': str(_LOGS_DIR / 'realty.log'),
        'formatter': 'verbose',
    }
    _handler_list = ['console', 'file']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {'format': '{levelname} {asctime} {module} {message}', 'style': '{'},
        'simple': {'format': '{levelname} {asctime} {message}', 'style': '{'},
    },
    'handlers': _log_handlers,
    'root': {'handlers': _handler_list, 'level': LOG_LEVEL},
    'loggers': {
        'django': {'handlers': _handler_list, 'level': 'WARNING', 'propagate': False},
        'properties': {'handlers': _handler_list, 'level': LOG_LEVEL, 'propagate': False},
        'users': {'handlers': _handler_list, 'level': LOG_LEVEL, 'propagate': False},
    },
}
