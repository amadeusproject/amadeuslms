from django.contrib import admin

from .models import Link

class LinkAdmin(admin.ModelAdmin):
	list_display = ['name', 'link','description']
	search_fields = ['name', 'link','description']


admin.site.register(Link, LinkAdmin)
