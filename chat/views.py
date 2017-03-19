from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator, EmptyPage
from django.http import Http404
from django.views import generic
from django.contrib import messages
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse, reverse_lazy
import textwrap
from django.utils.html import strip_tags
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

from channels import Group
import json

from categories.models import Category
from subjects.models import Subject
from users.models import User

from .models import Conversation, GeneralTalk, CategoryTalk, SubjectTalk, TalkMessages, ChatVisualizations
from .forms import ChatMessageForm

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
		search = self.request.GET.get('search', '')

		users = User.objects.filter(Q(username__icontains = search) | Q(last_name__icontains = search) | Q(social_name__icontains = search) | Q(email__icontains = search)).distinct().order_by('social_name','username').exclude(email = user.email)
		
		self.totals['general'] = ChatVisualizations.objects.filter(user = user, viewed = False, message__talk__generaltalk__isnull = False).count()
		self.totals['category'] = ChatVisualizations.objects.filter(user = user, viewed = False, message__talk__categorytalk__isnull = False).count()
		self.totals['subject'] = ChatVisualizations.objects.filter(user = user, viewed = False, message__talk__subjecttalk__isnull = False).count()

		return users

	def get_context_data(self, **kwargs):
		context = super(GeneralParticipants, self).get_context_data(**kwargs)

		context['title'] = _('Messages - Participants')
		context['totals'] = self.totals
		context['search'] = self.request.GET.get('search')
		context['chat_menu_active'] = 'subjects_menu_active'
		
		return context

class ParticipantProfile(LoginRequiredMixin, generic.DetailView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	model = User
	slug_field = 'email'
	slug_url_kwarg = 'email'
	context_object_name = 'participant'
	template_name = 'chat/_profile.html'

	def get_context_data(self, **kwargs):
		context = super(ParticipantProfile, self).get_context_data(**kwargs)

		context['space'] = self.request.GET.get('space', '0')
		context['space_type'] = self.request.GET.get('space_type', 'general')
		
		return context

class GetTalk(LoginRequiredMixin, generic.ListView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	context_object_name = 'messages'
	template_name = 'chat/talk.html'
	paginate_by = 20
	talk_id = "-1"

	def get_queryset(self):
		user = self.request.user
		user_email = self.kwargs.get('email', '')

		talks = Conversation.objects.filter((Q(user_one = user) & Q(user_two__email = user_email)) | (Q(user_two = user) & Q(user_one__email = user_email)))

		messages = TalkMessages.objects.none()

		if talks.count() > 0:
			talk = talks[0]
			self.talk_id = talk.id

			messages = TalkMessages.objects.filter(talk = talk).order_by('-create_date')

		return messages

	def get_context_data(self, **kwargs):
		context = super(GetTalk, self).get_context_data(**kwargs)

		user_email = self.kwargs.get('email', '')

		context['participant'] = get_object_or_404(User, email = user_email)
		context['talk_id'] = self.talk_id
		context['space'] = self.request.GET.get('space', '0')
		context['space_type'] = self.request.GET.get('space_type', 'general')
		
		return context

class SendMessage(LoginRequiredMixin, generic.edit.CreateView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	form_class = ChatMessageForm
	template_name = "chat/_form.html"

	def form_invalid(self, form):
		context = super(SendMessage, self).form_invalid(form)
		context.status_code = 400

		return context

	def form_valid(self, form):
		self.object = form.save(commit = False)

		self.object.user = self.request.user

		talk_id = self.kwargs.get('talk_id', '-1')
		user = get_object_or_404(User, email = self.kwargs.get('email', ''))
		space_type = self.kwargs.get('space_type', 'general')
		space = self.kwargs.get('space', 0)

		if talk_id == "-1":
			if space_type == 'general':
				talk = GeneralTalk.objects.create(user_one = self.request.user, user_two = user, space = 0)
			elif space_type == 'category':
				cat = get_object_or_404(Category, id = space)
				talk = CategoryTalk.objects.create(user_one = self.request.user, user_two = user, space = cat)
			else:
				sub = get_object_or_404(Subject, id = space)
				talk = SubjectTalk.objects.create(user_one = self.request.user, user_two = user, space = sub)
		else:
			talk = get_object_or_404(Conversation, id = talk_id)

		self.object.talk = talk

		self.object.save()

		simple_notify = textwrap.shorten(strip_tags(self.object.text), width = 30, placeholder = "...")

		if self.object.image:
			simple_notify += " ".join(_("[Photo]"))

		notification = {
			"type": "chat",
			"subtype": space_type,
			"user_icon": self.object.user.image_url,
			"notify_title": str(self.object.user),
			"simple_notify": simple_notify,
			"complete": render_to_string("chat/_message.html", {"talk_msg": self.object}, self.request),
			"container": "chat-" + str(self.object.user.id)
		}

		notification = json.dumps(notification)

		Group("user-%s" % user.id).send({'text': notification})

		ChatVisualizations.objects.create(viewed = False, message = self.object, user = user)

		return super(SendMessage, self).form_valid(form)

	def get_context_data(self, **kwargs):
		context = super(SendMessage, self).get_context_data(**kwargs)

		context['form_url'] = reverse_lazy('chat:create', args = (), kwargs = {'email': self.kwargs.get('email', ''), 'talk_id': self.kwargs.get('talk_id', None), 'space': self.kwargs.get('space', '0'), 'space_type': self.kwargs.get('space_type', 'general')})
		
		return context

	def get_success_url(self):
		return reverse_lazy('chat:render_message', args = (self.object.id, ))

def render_message(request, talk_msg):
	msg = get_object_or_404(TalkMessages, id = talk_msg)

	context = {}
	context['talk_msg'] = msg
	
	message = _('Message sent successfully!')
	
	html = render_to_string("chat/_message.html", context, request)

	return JsonResponse({'message': message, 'view': html, 'new_id': msg.id})