"""
Base settings for munsons project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""
import environ
import os

ROOT_DIR = environ.Path(__file__) - 3
APPS_DIR = ROOT_DIR.path('armour')

# Load operating system environment variables and then prepare to use them
env = environ.Env()

env_file = str(ROOT_DIR.path('.env'))
env.read_env(env_file)

# APP CONFIGURATION
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    # Default Django apps:
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # Admin
    'django.contrib.admin',
    'django.contrib.flatpages',
]
"""
Clark: replace djcelery with celery since now just use celery 5.2.0
"""
THIRD_PARTY_APPS = [
    'crispy_forms',
    'corsheaders',
    'django_countries',
    'tabbed_admin',
    'nested_inline',
    'ckeditor',
    'captcha',
    'wkhtmltopdf',
    'django_bleach',
    # 'djcelery',
    'celery',
    'loginas',
]

# Apps specific for this project go here.
LOCAL_APPS = [
    'armour.user',
    'armour.general',
    'armour.company',
    'armour.legislation',
]

# See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# MIDDLEWARE CONFIGURATION
# ------------------------------------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django_currentuser.middleware.ThreadLocalUserMiddleware',
]

# DEBUG
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool('DJANGO_DEBUG', False)

# EMAIL CONFIGURATION
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='')
EMAIL_SUBJECT_PREFIX = env('EMAIL_SUBJECT_PREFIX', default='[Operationarmour]')
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", True)
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST', default='')
EMAIL_PORT = env.int('EMAIL_PORT', 587)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
EMAIL_CONTACT_ADMINS = env.list('EMAIL_CONTACT_ADMINS', default=[])

# MANAGER CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = [
    ('AJ', 'aj@yoyo.org'),
]

# See: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS

ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=[])

# DATABASE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
# Uses django-environ to accept uri format
# See: https://django-environ.readthedocs.io/en/latest/#supported-types
DATABASES = {
    'default': env.db('DATABASE_URL', default='postgres:///db'),
}
DATABASES['default']['ATOMIC_REQUESTS'] = True
DATABASES['default']['CONN_MAX_AGE'] = 60
DATABASES['default']['ASYNC'] = 1
DATABASES['default']['ENGINE'] = 'django_postgrespool2'
DATABASES['default']['keepalives'] = 1
DATABASES['default']['keepalives_idle'] = 30
DATABASES['default']['keepalives_interval'] = 10
DATABASES['default']['keepalives_count'] = 5
DATABASE_POOL_ARGS = {
    'max_overflow': 100,
    'pool_size': 20,
    'recycle': 300
}

# GENERAL CONFIGURATION
# ------------------------------------------------------------------------------
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/London'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = 'en-GB'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = False

USE_THOUSAND_SEPARATOR = True
THOUSAND_SEPARATOR = ","
DECIMAL_SEPARATOR = "."

# TEMPLATE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        'DIRS': [
            str(APPS_DIR.path('templates')),
        ],
        'OPTIONS': {
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
            'debug': DEBUG,
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'armour.general.context_processors.general',
                # Your stuff: custom template context processors go here
            ],
        },
    },
]

# STATIC FILE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(ROOT_DIR('staticfiles'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [
    str(APPS_DIR.path('static')),
]

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# MEDIA CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(APPS_DIR('media'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = '/media/'

# URL Configuration
# ------------------------------------------------------------------------------
ROOT_URLCONF = 'config.urls'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = 'config.wsgi.application'

# PASSWORD STORAGE SETTINGS
# ------------------------------------------------------------------------------
# See https://docs.djangoproject.com/en/dev/topics/auth/passwords/#using-argon2-with-django
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
]

# PASSWORD VALIDATION
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
# ------------------------------------------------------------------------------

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

# AUTHENTICATION CONFIGURATION
# ------------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# Custom user app defaults
# Select the correct user model
AUTH_USER_MODEL = 'user.User'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'panel'
LOGOUT_URL = 'logout'

# Location of root django.contrib.admin URL, use {% url 'admin:index' %}
ADMIN_URL = r'^admin/'

if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOWED_ORIGINS = ['https://app.armour.ai', 'https://armour.ai', 'http://armour.ai', 'http://app.armour.ai']

CORS_ALLOW_HEADERS = (
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
)

STRIPE_PUB_KEY = env('STRIPE_PUB_KEY', default="pk_test_OfszO4Y8ZJV2gUHbgVwkxJs700qagt2DWH")
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY', default="sk_test_3hkxfECYKPyqkJ8dbzqKyTg400SLL6KX35")
STRIPE_TOKEN_KEY = env('STRIPE_TOKEN_KEY', default="rk_test_o2y2CRmbFomckaAOgLS7oYkE00FaPPFU8J")

IS_HTTPS = env.bool('IS_HTTPS', default=False)

RAVEN_DSN = env('RAVEN_DSN', default=None)

CKEDITOR_UPLOAD_PATH = "%s/ckeditor" % MEDIA_ROOT

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline',
             'Strike', 'Subscript', 'Superscript', '-', 'Undo', 'Redo', '-'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'JustifyLeft', 'JustifyCenter',
             'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink', 'Image', ],
            ['Source']
        ]
    }
}

# Which HTML tags are allowed
BLEACH_ALLOWED_TAGS = ['p', 'b', 'i', 'u', 'em', 'a', 'ul', 'li', 'ol', 'b', 'br', 'span', 'div', 's', 'sup', 'strong']

# Which HTML attributes are allowed
BLEACH_ALLOWED_ATTRIBUTES = ['href', 'title', 'style', 'target']

# Which CSS properties are allowed in 'style' attributes (assuming
# style is an allowed attribute)
BLEACH_ALLOWED_STYLES = ['font-weight', 'text-decoration', 'font-variant', ]

# Strip unknown tags if True, replace with HTML escaped characters if
# False
BLEACH_STRIP_TAGS = True

# Strip comments, or leave them in.
BLEACH_STRIP_COMMENTS = False
BLEACH_DEFAULT_WIDGET = 'ckeditor.widgets.CKEditorWidget'

TABBED_ADMIN_USE_JQUERY_UI = True

RECAPTCHA_PUBLIC_KEY = env('RECAPTCHA_PUBLIC_KEY', default='6Ldh-6kUAAAAABFnb43TvKL8TrupthyrK3uRl0yM')
RECAPTCHA_PRIVATE_KEY = env('RECAPTCHA_PRIVATE_KEY', default='6Ldh-6kUAAAAAHyTGIrXup5q5ESAo112JNpXj7eJ')

USE_HTTPS = env.bool("USE_HTTPS", default=False)

SESSION_COOKIE_AGE = env.int("SESSION_COOKIE_AGE", default=28800)
SESSION_COOKIE_NAME = 'armour-app'
SESSION_COOKIE_SECURE = USE_HTTPS
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
WKHTMLTOPDF_CMD = env("WKHTMLTOPDF_CMD", default='xvfb-run -a /usr/bin/wkhtmltopdf')

REGISTARTION_VIEW = env.bool("REGISTARTION_VIEW", default=True)

MAX_UPLOAD_SIZE = env.int("MAX_UPLOAD_SIZE", default=10485760)

COUNTRIES_OVERRIDE = {
    'IE': 'Republic of Ireland',
}

COUNTRIES_ONLY = ['GB', 'IE']

FREE_STANDARD_LIMIT = env.int("FREE_STANDARD_LIMIT", default=5)
FREE_USER_LIMIT = env.int("FREE_USER_LIMIT", 3)
FREE_DAYS = env.int("FREE_DAYS", default=14)

NC_LEGAL = env.list("NC_LEGAL", default=[])
BLOCK_SOURCE = env.bool("BLOCK_SOURCE", default=False)

########## CELERY

# import djcelery
from celery import Celery
from celery.schedules import crontab
app = Celery()
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# djcelery.setup_loader()
CELERYBEAT_SCHEDULER = 'celery.schedulers.DatabaseScheduler'
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = 'celery.backends.database.DatabaseBackend'
########## END CELERY

if RAVEN_DSN:
    import raven

    INSTALLED_APPS += ['raven.contrib.django.raven_compat', ]
    RAVEN_CONFIG = {
        'dsn': RAVEN_DSN,
        'release': raven.fetch_git_sha(os.path.dirname(os.pardir)),
    }
