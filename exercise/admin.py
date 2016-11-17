from django.contrib import admin
from .models import Exercise, File

class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

class FileAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

admin.site.register(Exercise, ExerciseAdmin)
admin.site.register(File, ExerciseAdmin)
