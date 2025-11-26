# config/settings.py

from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-ed1n=#-fkjxj9-8ucm-6-rp+t7t@^@gm*v(du!-r9$4@6#_&67')

DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',') if os.getenv('ALLOWED_HOSTS') else []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'axes',
    'core',
    'accounts',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'core.middleware.RequestIDMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "front" / "client" / "dist"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith('postgresql'):
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(default=DATABASE_URL, conn_max_age=600)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "front" / "client" / "dist"]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'EXCEPTION_HANDLER': 'core.exceptions.custom_exception_handler',
}

if DEBUG:
    LOGS_DIR = BASE_DIR / 'logs'
    if not LOGS_DIR.exists():
        LOGS_DIR.mkdir()
    LOG_FILE_PATH = LOGS_DIR / 'django.log'
    USE_FILE_LOGGING = True
else:
    LOG_FILE_PATH = '/var/log/django/app.log'
    
    import pathlib
    log_dir = pathlib.Path(LOG_FILE_PATH).parent
    USE_FILE_LOGGING = False
    
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        test_file = log_dir / '.write_test'
        test_file.touch()
        test_file.unlink()
        USE_FILE_LOGGING = True
    except (PermissionError, OSError) as e:
        print(f"WARNING: Cannot write to {log_dir}, file logging disabled: {e}")
        LOGS_DIR = BASE_DIR / 'logs'
        LOGS_DIR.mkdir(exist_ok=True)
        LOG_FILE_PATH = LOGS_DIR / 'django.log'
        USE_FILE_LOGGING = True

handlers_config = {
    'console': {
        'class': 'logging.StreamHandler',
        'formatter': 'verbose' if DEBUG else 'simple',
    },
}

if USE_FILE_LOGGING:
    handlers_config['file'] = {
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': LOG_FILE_PATH,
        'maxBytes': 1024 * 1024 * 1,
        'backupCount': 4,
        'formatter': 'verbose',
    }

if DEBUG:
    active_handlers = ['console']
else:
    active_handlers = ['console', 'file'] if USE_FILE_LOGGING else ['console']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} | {name} | {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {message}',
            'style': '{',
        },
    },
    'handlers': handlers_config,
    'root': {
        'handlers': active_handlers,
        'level': 'DEBUG' if DEBUG else 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': active_handlers,
            'level': 'INFO',
            'propagate': False,
        },
        'core.middleware': {
            'handlers': active_handlers,
            'level': 'INFO',
            'propagate': False,
        },
        'core.exceptions': {
            'handlers': active_handlers,
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

AUTH_USER_MODEL = 'accounts.CustomUser'

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',  # AxesStandaloneBackend
    'django.contrib.auth.backends.ModelBackend',
]

# Django Axes - Admin Login Protection
AXES_ENABLED = True
AXES_FAILURE_LIMIT = 3
AXES_COOLOFF_TIME = 24  # 24 sata
AXES_LOCK_OUT_AT_FAILURE = True
AXES_ONLY_ADMIN_SITE = True