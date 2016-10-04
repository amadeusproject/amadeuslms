from django.contrib import admin

from .models import Poll, Answer

class PollAdmin(admin.ModelAdmin):
	list_display = ['name', 'slug','limit_date']
	search_fields = ['name','slug']

class AnswerAdmin(admin.ModelAdmin):
	list_display = ['answer','order']
	search_fields = ['answer']

admin.site.register(Poll, PollAdmin)
admin.site.register(Answer, AnswerAdmin)
