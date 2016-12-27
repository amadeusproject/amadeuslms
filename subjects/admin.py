
from django.contrib import admin
from .models import Subject, Marker
from .forms import CreateSubjectForm, CreateMarkerForm

class SubjectAdmin(admin.ModelAdmin):
	list_display = ['name', 'description_brief', 'description', 'init_date', 'end_date', 'visible', 'professor',]
	search_fields = ['name']
	form = CreateSubjectForm


class MarkerAdmin(admin.ModelAdmin):
	list_display = ['name']
	search_fields = ['name']
	form = CreateMarkerForm

admin.site.register(Subject, SubjectAdmin)
admin.site.register(Marker, MarkerAdmin)

