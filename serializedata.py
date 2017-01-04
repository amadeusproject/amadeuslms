from django.core import serializers
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "amadeus.settings")

from subjects.models import Subject


data = serializers.serialize("json", Subject.objects.all())
print(data)