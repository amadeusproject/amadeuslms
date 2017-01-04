from django.contrib import admin

from .models import Log

class LogAdmin(admin.ModelAdmin):
	list_display = ['datetime', 'user', 'user_email', 'action', 'resource', 'context']
	search_fields = ['user', 'action', 'resource']

admin.site.register(Log, LogAdmin)