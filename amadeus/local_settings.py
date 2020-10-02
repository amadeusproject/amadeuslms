import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'amadeuslms',
        'USER': 'amadeus',
        'PASSWORD': 'amadeuslms',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "asgi_redis.RedisChannelLayer",
        "CONFIG": {"hosts": [("localhost", 6379)], },
        "ROUTING": "amadeus.routing.channel_routing",
    }
}

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

FILE_UPLOAD_PERMISSIONS = 0o644

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/home/amadeus/django_debug.log'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True
        },
    }
}
