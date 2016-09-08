from django.contrib import admin

from .models import Category, Course, Subject,Topic

class CategoryAdmin(admin.ModelAdmin):
	list_display = ['name', 'slug']
	search_fields = ['name', 'slug']

class CourseAdmin(admin.ModelAdmin):
	list_display = ['name', 'slug']
	search_fields = ['name', 'slug']

class SubjectAdmin(admin.ModelAdmin):
	list_display = ['name', 'slug']
	search_fields = ['name', 'slug']

class TopicAdmin(admin.ModelAdmin):
	list_display = ['name', 'slug']
	search_fields = ['name', 'slug']

admin.site.register(Category, CategoryAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Topic, TopicAdmin)
