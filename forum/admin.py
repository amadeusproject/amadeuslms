from django.contrib import admin

from .models import Forum, Post, PostAnswer

class ForumAdmin(admin.ModelAdmin):
	list_display = ['name', 'slug']
	search_fields = ['name', 'slug']

class PostAdmin(admin.ModelAdmin):
	list_display = ['user', 'forum']
	search_fields = ['user', 'forum']

class PostAnswerAdmin(admin.ModelAdmin):
	list_display = ['user', 'post', 'answer_date']
	search_fields = ['user']

admin.site.register(Forum, ForumAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(PostAnswer, PostAnswerAdmin)