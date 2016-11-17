from django.contrib import admin
from .models import Exercise

class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['name_exercise']
    search_fields = ['name_exercise']

admin.site.register(Exercise, ExerciseAdmin)
