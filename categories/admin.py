from django.contrib import admin
from .models import Category
from .forms import CategoryForm

class CategoryAdmin(admin.ModelAdmin):
	list_display = ['name', 'description', 'visible',
	]
	search_fields = ['name']
	form = CategoryForm

admin.site.register(Category, CategoryAdmin)