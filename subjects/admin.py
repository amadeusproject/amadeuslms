
from django.contrib import admin
from .models import Subject, Tag
from .forms import CreateSubjectForm, CreateTagForm

class SubjectAdmin(admin.ModelAdmin):
	list_display = ['name', 'description_brief', 'description', 'init_date', 'end_date', 'visible', 'category']
	search_fields = ['name']
	


class TagAdmin(admin.ModelAdmin):
	list_display = ['name']
	search_fields = ['name']
	form = CreateTagForm

admin.site.register(Subject, SubjectAdmin)
admin.site.register(Tag, TagAdmin)

