from django.contrib import admin

from .models import Exam, Answer, AnswersStudent

class ExamAdmin(admin.ModelAdmin):
	list_display = ['name', 'slug','begin_date','limit_date']
	search_fields = ['name','slug']

class AnswerAdmin(admin.ModelAdmin):
	list_display = ['answer','order']
	search_fields = ['answer']

class AnswersStudentAdmin(admin.ModelAdmin):
	list_display = ['student','exam','answered_in']
	search_fields = ['student','exam']

admin.site.register(Exam, ExamAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(AnswersStudent, AnswersStudentAdmin)
