from django.core import serializers
import os
import json
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "amadeus.settings")

from subjects.models import Subject
from users.models import User
from categories.models import Category

subject_data = serializers.serialize("json", Subject.objects.all())


users_data = serializers.serialize("json", User.objects.all())

category_data = serializers.serialize("json", Category.objects.all())

with open('data.txt', 'w') as outfile:
    json.dump(category_data, outfile)