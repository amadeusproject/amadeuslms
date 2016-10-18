from django.contrib import admin

from .models import Link

class LinkAdmin(admin.ModelAdmin):
	list_display = ['name', 'link_url','link_description']
	search_fields = ['name', 'link_url','link_description']


admin.site.register(Link, LinkAdmin)
