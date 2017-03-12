from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator, EmptyPage
from django.http import Http404
from django.views import generic
from django.contrib import messages
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

from users.models import User

from .models import Conversation, ChatVisualizations

class GeneralIndex(LoginRequiredMixin, generic.ListView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'chat/list.html'
	context_object_name = "conversations"
	paginate_by = 10

	totals = {}

	def get_queryset(self):
		user = self.request.user
		page = self.request.GET.get('page', False)

		conversations = Conversation.objects.filter(Q(user_one = user) | Q(user_two = user))
		
		self.totals['general'] = ChatVisualizations.objects.filter(user = user, viewed = False, message__talk__generaltalk__isnull = False).count()
		self.totals['category'] = ChatVisualizations.objects.filter(user = user, viewed = False, message__talk__categorytalk__isnull = False).count()
		self.totals['subject'] = ChatVisualizations.objects.filter(user = user, viewed = False, message__talk__subjecttalk__isnull = False).count()

		return conversations

	def get_context_data(self, **kwargs):
		context = super(GeneralIndex, self).get_context_data(**kwargs)

		context['title'] = _('Messages')
		context['totals'] = self.totals
		context['chat_menu_active'] = 'subjects_menu_active'
		
		return context

class GeneralParticipants(LoginRequiredMixin, generic.ListView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'chat/list_participants.html'
	context_object_name = "participants"
	paginate_by = 10

	totals = {}

	def get_queryset(self):
		user = self.request.user

		users = User.objects.all().exclude(id = user.id)
		
		self.totals['general'] = ChatVisualizations.objects.filter(user = user, viewed = False, message__talk__generaltalk__isnull = False).count()
		self.totals['category'] = ChatVisualizations.objects.filter(user = user, viewed = False, message__talk__categorytalk__isnull = False).count()
		self.totals['subject'] = ChatVisualizations.objects.filter(user = user, viewed = False, message__talk__subjecttalk__isnull = False).count()

		return users

	def get_context_data(self, **kwargs):
		context = super(GeneralParticipants, self).get_context_data(**kwargs)

		context['title'] = _('Messages - Participants')
		context['totals'] = self.totals
		context['chat_menu_active'] = 'subjects_menu_active'
		
		return context