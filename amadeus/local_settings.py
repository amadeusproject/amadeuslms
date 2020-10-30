import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "amadeus",
        "USER": "amadeus_admin",
        "PASSWORD": "amadeus",
        "HOST": "db",
        "PORT": "5432",
    }
}

STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "asgiref.inmemory.ChannelLayer",
        "ROUTING": "amadeus.routing.channel_routing",
    }
}
