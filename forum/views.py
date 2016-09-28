from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Forum, Post, PostAnswer
from courses.models import Topic

from .forms import ForumForm

class ForumIndex(LoginRequiredMixin, generic.ListView):
	login_url = reverse_lazy("core:home")	
	redirect_field_name = 'next'

	template_name = "forum/forum_list.html"
	context_object_name = 'forum'

	def get_queryset(self):
		forum_id = self.request.GET.get('forum_id', 0)

		context = Forum.objects.get(id = forum_id)

		return context

class CreateForumView(LoginRequiredMixin, generic.edit.CreateView):

	template_name = 'forum/forum_form.html'
	form_class = ForumForm
	success_url = reverse_lazy('forum:index')

class PostIndex(LoginRequiredMixin, generic.ListView):
	login_url = reverse_lazy("core:home")	
	redirect_field_name = 'next'

	template_name = "post/post_list.html"
	context_object_name = 'posts'

	def get_queryset(self):
		forum = get_object_or_404(Forum, slug = self.request.GET.get('forum', ''))

		context = Post.objects.filter(forum = forum)

		return context

class PostAnswerIndex(LoginRequiredMixin, generic.ListView):
	login_url = reverse_lazy("core:home")	
	redirect_field_name = 'next'

	template_name = "post_answers/post_answer_list.html"
	context_object_name = 'answers'

	def get_queryset(self):
		post = get_object_or_404(Post, id = self.request.GET.get('post', ''))

		context = PostAnswer.objects.filter(post = post)

		return context