from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Forum
from courses.models import Topic

class ForumIndex(LoginRequiredMixin, ListView):
	login_url = reverse_lazy("core:home")	
	redirect_field_name = 'next'

	template_name = "forum_list.html"
	context_object_name = 'forum'

	def get_queryset(self):
		topic = get_object_or_404(Topic, slug = self.request.GET.get('topic', ''))

		context = Forum.objects.filter(topic = topic)

		return context
