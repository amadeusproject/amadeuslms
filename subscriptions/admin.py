from django.contrib import admin

from .models import Subscribe

class SubscribeAdmin(admin.ModelAdmin):
	list_display = ['user', 'course']
	search_fields = ['user', 'course']

admin.site.register(Subscribe, SubscribeAdmin)