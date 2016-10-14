from django.contrib import admin

from .models import Exam, Answer

class ExamAdmin(admin.ModelAdmin):
	list_display = ['name', 'slug','begin_date','limit_date']
	search_fields = ['name','slug']

class AnswerAdmin(admin.ModelAdmin):
	list_display = ['answer','order']
	search_fields = ['answer']

admin.site.register(Exam, ExamAdmin)
admin.site.register(Answer, AnswerAdmin)
