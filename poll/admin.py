from django.contrib import admin

from .models import Poll, Answer, AnswersStudent

class PollAdmin(admin.ModelAdmin):
	list_display = ['name', 'slug','limit_date']
	search_fields = ['name','slug']

class AnswerAdmin(admin.ModelAdmin):
	list_display = ['answer','order']
	search_fields = ['answer']

class AnswersStudentAdmin(admin.ModelAdmin):
	list_display = ['student','poll','answered_in']
	search_fields = ['student','poll']

admin.site.register(Poll, PollAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(AnswersStudent, AnswersStudentAdmin)
