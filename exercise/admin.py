from django.contrib import admin
from .models import Exercise, File

class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['name_exercise']
    search_fields = ['name_exercise']

class FileAdmin(admin.ModelAdmin):
    list_display = ['name_file']
    search_fields = ['name_file']

admin.site.register(Exercise, ExerciseAdmin)
admin.site.register(File, FileAdmin)
