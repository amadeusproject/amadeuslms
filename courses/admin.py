from django.contrib import admin

from .models import CourseCategory, Course, Subject, Topic, Activity, Material, CategorySubject

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name', 'slug']

class CategorySubjectAdmin(admin.ModelAdmin):
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

class ActivityAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name', 'slug']

class MaterialAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name', 'slug']

admin.site.register(CourseCategory, CategoryAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(Material, MaterialAdmin)
admin.site.register(CategorySubject, CategorySubjectAdmin)
