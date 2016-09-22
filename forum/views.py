from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Forum, Post
from courses.models import Topic

from .forms import ForumForm

class ForumIndex(LoginRequiredMixin, generic.ListView):
	login_url = reverse_lazy("core:home")	
	redirect_field_name = 'next'

	template_name = "forum_list.html"
	context_object_name = 'foruns'

	def get_queryset(self):
		topic = get_object_or_404(Topic, slug = self.request.GET.get('topic', ''))

		context = Forum.objects.filter(topic = topic)

		return context

class CreateForumView(LoginRequiredMixin, generic.edit.CreateView):

	template_name = 'forum_form.html'
	form_class = ForumForm
	success_url = reverse_lazy('forum:index')

class PostIndex(LoginRequiredMixin, generic.ListView):
	login_url = reverse_lazy("core:home")	
	redirect_field_name = 'next'

	template_name = "post_list.html"
	context_object_name = 'posts'

	def get_queryset(self):
		forum = get_object_or_404(Forum, slug = self.request.GET.get('forum', ''))

		context = Post.objects.filter(forum = forum)

		return context