from django.contrib import admin
from .models import News
# Register your models here.

class NewsAdmin(admin.ModelAdmin):
	list_display = ['title', 'slug', 'creator', 'create_date']
	search_fields = ['title']

admin.site.register(News, NewsAdmin)
