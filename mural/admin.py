from django.contrib import admin

from .models import MuralVisualizations
# Register your models here.

class MuralAdmin(admin.ModelAdmin):
	list_display = ['user', 'viewed', 'post', 'comment', 'date_viewed']

admin.site.register(MuralVisualizations, MuralAdmin)