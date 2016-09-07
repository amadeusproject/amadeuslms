from django.contrib import admin

from .models import Action, Resource, Action_Resource

class ActionAdmin(admin.ModelAdmin):
	list_display = ['name', 'created_date']
	search_fields = ['name', 'created_date']

class ResourceAdmin(admin.ModelAdmin):
	list_display = ['name', 'created_date']
	search_fields = ['name', 'created_date']

class ActionResourceAdmin(admin.ModelAdmin):
	list_display = ['action', 'resource']
	search_fields = ['action', 'resource']

admin.site.register(Action, ActionAdmin)
admin.site.register(Resource, ResourceAdmin)
admin.site.register(Action_Resource, ActionResourceAdmin)