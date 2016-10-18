from django.contrib import admin

from .models import TopicFile
class TopicFileAdmin(admin.ModelAdmin):
	list_display = ['name', 'slug']
	search_fields = ['name', 'slug']

admin.site.register(TopicFile, TopicFileAdmin)
