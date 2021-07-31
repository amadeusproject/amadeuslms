""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

import os

import dj_database_url

from django.conf.global_settings import DATETIME_INPUT_FORMATS, DATE_INPUT_FORMATS
from django.utils.translation import ugettext_lazy as _

db_from_ev = dj_database_url.config(conn_max_age=500)


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "$=8)c!5)iha85a&8q4+kv1pyg0yl7_xe_x^z=2cn_1d7r0hny4"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "widget_tweaks",
    "rolepermissions",
    "oauth2_provider",
    "rest_framework",
    "rest_framework_swagger",
    "django_filters",
    "django_bootstrap_breadcrumbs",
    "django_summernote",
    "session_security",
    "django_crontab",
    "django_cron",
    #"channels",
    "file_resubmit",  # Utilizado para salvar arquivos na cache, para caso o formulario não seja preenchido corretamente o usuário não precise fazer o upload outra vez dos arquivos
    "fcm_django",
    "amadeus",
    "users",
    "notifications",
    "log",
    "categories",
    "subjects",
    "students_group",
    "topics",
    "pendencies",
    "mural",
    "chat",
    "file_link",
    "goals",
    "pdf_file",
    "links",
    "webpage",
    "youtube_video",
    "mailsender",
    "security",
    "themes",
    "api",
    "reports",
    "webconference",
    "news",
    "analytics",
    "dashboards",
    "bulletin",
    "banco_questoes",
    "questionary",
    "h5p",
    "material_delivery",
    "elastic",
    "environment_creation",
    'datatableview',
]

MIDDLEWARE_CLASSES = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.auth.middleware.SessionAuthenticationMiddleware",
    "users.middleware.SessionExpireMiddleware",
    "session_security.middleware.SessionSecurityMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "log.middleware.TimeSpentMiddleware",
    # libs-middleware
]

ROOT_URLCONF = "amadeus.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "amadeus.context_processors.theme",
                "amadeus.context_processors.notifies",
                "amadeus.context_processors.mural_notifies",
                "amadeus.context_processors.chat_notifies",
            ],
            "debug": True,
        },
    },
]


CACHES = {
    "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache",},
    "file_resubmit": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": os.path.join(BASE_DIR, "data/cache/resubmit"),
    },
}

WSGI_APPLICATION = "amadeus.wsgi.application"

SESSION_SECURITY_WARN_AFTER = 3300
SESSION_SECURITY_EXPIRE_AFTER = 3600
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
# Database
# https://docs.djangopr/*oject.com/en/1.9/ref/settings/#databases

DATABASES = {
    "default": db_from_ev,
}


# superuser: admin pass: amadeus2358

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = "pt-br"

LANGUAGES = [
    ("pt-br", _("Portuguese")),
    ("en", _("English")),
]

TIME_ZONE = "America/Recife"

USE_I18N = True

USE_L10N = True

USE_TZ = True

FORMAT_MODULE_PATH = "amadeus.formats"
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = "/static/"

# Static files heroku
STATIC_ROOT = os.path.join(PROJECT_ROOT, "staticfiles")

STATICFILES_STORAGE = "whitenoise.django.GzipManifestStaticFilesStorage"

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "amadeus/static"),
    os.path.join(BASE_DIR, "bulletin/static"),
]

CRON_CLASSES = ["notifications.cron.Notify", "goals.cron.SetGoals"]

CRONJOBS = [
    ("30 5 * * *", "notifications.cron.notification_cron"),
    ("0 0 * * *", "goals.cron.setgoals_cron"),
]

# SECURITY
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Allow all host headers
ALLOWED_HOSTS = ["*"]

# Files
MEDIA_ROOT = os.path.join(PROJECT_ROOT, "uploads")
MEDIA_URL = "/uploads/"


# Users
LOGIN_REDIRECT_URL = "subjects:home"
LOGIN_URL = "users:login"
AUTH_USER_MODEL = "users.User"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]
ROLEPERMISSIONS_MODULE = "amadeus.roles"

LOGS_URL = "logs/"
# https://github.com/squ1b3r/Djaneiro


# E-mail
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# DEFAULT_FROM_EMAIL = 'admin@amadeus.com.br'

# Messages
from django.contrib.messages import constants as messages_constants

MESSAGE_TAGS = {
    messages_constants.DEBUG: "debug",
    messages_constants.INFO: "info",
    messages_constants.SUCCESS: "success",
    messages_constants.WARNING: "warning",
    messages_constants.ERROR: "danger",
}

# Send email for forgot Password
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = "amadeusteste@gmail.com"
# SERVER_EMAIL = 'amadeusteste@gmail.com'
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = "amadeusteste@gmail.com"
EMAIL_HOST_PASSWORD = "amadeusteste"
# SMTP CONFIG
# EMAIL_BACKEND = 'core.smtp.AmadeusEmailBackend'

# For date purposes
DATE_INPUT_FORMATS.append("%d/%m/%y")
DATE_INPUT_FORMATS.append("%m/%d/%y")

# API CONFIG STARTS
# TELL the rest framework to use a different backend
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "oauth2_provider.contrib.rest_framework.OAuth2Authentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
        "rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,  # pagination purposes
}

SWAGGER_SETTINGS = {
    "JSON_EDITOR": True,
}

OAUTH2_PROVIDER = {"SCOPES": {"read": "Read scope", "write": "Write scope"}}
# API CONFIG ENDS

# FILE UPLOAD
MAX_UPLOAD_SIZE = 10*1024*1024

SUMMERNOTE_CONFIG = {
    # Using SummernoteWidget - iframe mode
    "iframe": True,  # or set False to use SummernoteInplaceWidget - no iframe mode
    # Using Summernote Air-mode
    "airMode": False,
    # Use native HTML tags (`<b>`, `<i>`, ...) instead of style attributes
    # (Firefox, Chrome only)
    "styleWithTags": True,
    # Set text direction : 'left to right' is default.
    "direction": "ltr",
    # Change editor size
    "width": "100%",
    "height": "300",
    # Use proper language setting automatically (default)
    "lang": None,
    # Or, set editor language/locale forcely
    "lang_matches": {"pt": "pt-BR",},
    # Customize toolbar buttons
    "toolbar": [
        ["style", ["style"]],
        [
            "font",
            [
                "bold",
                "italic",
                "underline",
                "superscript",
                "subscript",
                "strikethrough",
                "clear",
            ],
        ],
        ["fontname", ["fontname"]],
        ["fontsize", ["fontsize"]],
        ["color", ["color"]],
        ["para", ["ul", "ol", "paragraph"]],
        ["height", ["height"]],
        ["table", ["table"]],
        ["insert", ["link", "picture", "video", "hr"]],
        ["view", ["fullscreen", "codeview"]],
        ["help", ["help"]],
    ],
    # Need authentication while uploading attachments.
    "attachment_require_authentication": True,
    # Set `upload_to` function for attachments.
    #'attachment_upload_to': my_custom_upload_to_func(),
}

#Debug Toolbar Config
INSTALLED_APPS += (
    'channels_panel',
    'debug_toolbar',
)

MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

INTERNAL_IPS = ('127.0.0.1', 'localhost')

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
    'channels_panel.panel.ChannelsDebugPanel',
]

def show_toolbar(request):
    return True

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    "SHOW_TOOLBAR_CALLBACK" : show_toolbar,
}

try:
    from .local_settings import *
except ImportError:
    pass
