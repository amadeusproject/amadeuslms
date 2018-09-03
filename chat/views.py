""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator, EmptyPage
from django.http import Http404
from django.views import generic
from django.contrib import messages
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse, reverse_lazy
import textwrap
from datetime import datetime
from django.utils import formats
from django.utils.html import strip_tags
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from amadeus.permissions import has_subject_view_permissions

from channels import Group
import json

from log.models import Log
from log.mixins import LogMixin
import time

from categories.models import Category
from subjects.models import Subject
from users.models import User

from api.utils import  sendChatPushNotification

from .models import Conversation, TalkMessages, ChatVisualizations, ChatFavorites
from .forms import ChatMessageForm

class GeneralIndex(LoginRequiredMixin, LogMixin, generic.ListView):
	log_component = "chat"
	log_action = "view"
	log_resource = "general"
	log_context = {}

	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'chat/list.html'
	context_object_name = "conversations"
	paginate_by = 10

	totals = {}

	def get_queryset(self):
		user = self.request.user

		conversations = Conversation.objects.extra(select = {"most_recent": "select create_date from chat_talkmessages where chat_talkmessages.talk_id = chat_conversation.id order by create_date DESC LIMIT 1"}).filter((Q(user_one = user) | Q(user_two = user))).order_by('-most_recent')
				
		return conversations

	def get_context_data(self, **kwargs):
		context = super(GeneralIndex, self).get_context_data(**kwargs)

		self.log_context['timestamp_start'] = str(int(time.time()))

		super(GeneralIndex, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		self.request.session['log_id'] = Log.objects.latest('id').id

		context['title'] = _('Messages')
		context['totals'] = self.totals
		context['chat_menu_active'] = 'subjects_menu_active'
		
		return context

class GeneralParticipants(LoginRequiredMixin, LogMixin, generic.ListView):
	log_component = "chat"
	log_action = "view"
	log_resource = "general_participants"
	log_context = {}

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
				
		return users

	def get_context_data(self, **kwargs):
		context = super(GeneralParticipants, self).get_context_data(**kwargs)

		self.log_context['search_by'] = self.request.GET.get('search', '')
		self.log_context['timestamp_start'] = str(int(time.time()))

		super(GeneralParticipants, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		self.request.session['log_id'] = Log.objects.latest('id').id

		context['title'] = _('Messages - Participants')
		context['totals'] = self.totals
		context['search'] = self.request.GET.get('search', '')
		context['chat_menu_active'] = 'subjects_menu_active'
		
		return context

class SubjectParticipants(LoginRequiredMixin, LogMixin, generic.ListView):
	log_component = "chat"
	log_action = "view"
	log_resource = "subject_participants"
	log_context = {}

	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'chat/subject_view_participants.html'
	context_object_name = "participants"
	paginate_by = 10

	def dispatch(self, request, *args,**kwargs):
		subject = get_object_or_404(Subject, id = kwargs.get('subject', 0))

		if not has_subject_view_permissions(request.user, subject):
			return redirect(reverse_lazy('subjects:home'))

		return super(SubjectParticipants, self).dispatch(request, *args, **kwargs)

	def get_queryset(self):
		user = self.request.user
		sub = self.kwargs.get('subject', 0)
		search = self.request.GET.get('search', '')

		users = User.objects.filter((Q(username__icontains = search) | Q(last_name__icontains = search) | Q(social_name__icontains = search) | Q(email__icontains = search)) & (Q(is_staff = True) | Q(subject_student__id = sub) | Q(professors__id = sub) | Q(coordinators__subject_category__id = sub))).distinct().order_by('social_name','username').exclude(email = user.email)
	
		return users

	def get_context_data(self, **kwargs):
		context = super(SubjectParticipants, self).get_context_data(**kwargs)

		sub = self.kwargs.get('subject', 0)
		subject = get_object_or_404(Subject, id = sub)

		self.log_context['subject_id'] = subject.id
		self.log_context['subject_name'] = subject.name
		self.log_context['subject_slug'] = subject.slug
		self.log_context['search_by'] = self.request.GET.get('search', '')
		self.log_context['timestamp_start'] = str(int(time.time()))

		super(SubjectParticipants, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		self.request.session['log_id'] = Log.objects.latest('id').id

		context['subject'] = subject
		context['search'] = self.request.GET.get('search', '')
		context['title'] = _('%s - Participants')%(str(subject))
		
		context['space'] = self.kwargs.get('subject', 0)
		context['space_type'] = 'subject'
		
		return context

class SubjectView(LoginRequiredMixin, LogMixin, generic.ListView):
	log_component = "chat"
	log_action = "view"
	log_resource = "subject"
	log_context = {}

	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'chat/subject_view.html'
	context_object_name = "conversations"
	paginate_by = 10

	def dispatch(self, request, *args,**kwargs):
		subject = get_object_or_404(Subject, slug = kwargs.get('slug', ''))

		if not has_subject_view_permissions(request.user, subject):
			return redirect(reverse_lazy('subjects:home'))

		return super(SubjectView, self).dispatch(request, *args, **kwargs)

	def get_queryset(self):
		user = self.request.user
		slug = self.kwargs.get('slug')
		subject = get_object_or_404(Subject, slug = slug)

		conversations = Conversation.objects.extra(select = {"most_recent": "select create_date from chat_talkmessages where chat_talkmessages.talk_id = chat_conversation.id order by create_date DESC LIMIT 1"}).filter((Q(user_one = user) & (Q(user_two__is_staff = True) | 
			Q(user_two__subject_student = subject) | Q(user_two__professors = subject) | Q(user_two__coordinators__subject_category = subject))) |
			(Q(user_two = user) & (Q(user_one__is_staff = True) | Q(user_one__subject_student = subject) |
			Q(user_one__professors = subject) | Q(user_one__coordinators__subject_category = subject)))).distinct().order_by('-most_recent')

		return conversations

	def get_context_data(self, **kwargs):
		context = super(SubjectView, self).get_context_data(**kwargs)

		slug = self.kwargs.get('slug', None)
		subject = get_object_or_404(Subject, slug = slug)

		self.log_context['subject_id'] = subject.id
		self.log_context['subject_name'] = subject.name
		self.log_context['subject_slug'] = subject.slug
		self.log_context['timestamp_start'] = str(int(time.time()))

		super(SubjectView, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		self.request.session['log_id'] = Log.objects.latest('id').id

		context['title'] = _('%s - Messages')%(str(subject))
		context['subject'] = subject
		
		return context

class ParticipantProfile(LoginRequiredMixin, LogMixin, generic.DetailView):
	log_component = "chat"
	log_action = "view"
	log_resource = "profile"
	log_context = {}

	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	model = User
	slug_field = 'email'
	slug_url_kwarg = 'email'
	context_object_name = 'participant'
	template_name = 'chat/_profile.html'

	def get_context_data(self, **kwargs):
		context = super(ParticipantProfile, self).get_context_data(**kwargs)

		self.log_context['user_id'] = self.object.id
		self.log_context['user_name'] = str(self.object)
		self.log_context['user_email'] = self.object.email

		super(ParticipantProfile, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		context['space'] = self.request.GET.get('space', '0')
		context['space_type'] = self.request.GET.get('space_type', 'general')
		
		return context

class GetTalk(LoginRequiredMixin, LogMixin, generic.ListView):
	log_component = "chat"
	log_action = "view"
	log_resource = "talk"
	log_context = {}

	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	context_object_name = 'messages'
	template_name = 'chat/talk.html'
	paginate_by = 20
	talk_id = "-1"
	n_viewed = 0

	def get_queryset(self):
		user = self.request.user
		user_email = self.kwargs.get('email', '')

		talks = Conversation.objects.filter((Q(user_one = user) & Q(user_two__email = user_email)) | (Q(user_two = user) & Q(user_one__email = user_email)))

		messages = TalkMessages.objects.none()

		if talks.count() > 0:
			talk = talks[0]
			self.talk_id = talk.id

			messages = TalkMessages.objects.filter(talk = talk).order_by('-create_date')

			views = ChatVisualizations.objects.filter(Q(user = user) & Q(viewed = False) & (Q(message__talk = talk)))
			self.n_viewed = views.count()
			views.update(viewed = True, date_viewed = datetime.now())

		return messages

	def get_context_data(self, **kwargs):
		context = super(GetTalk, self).get_context_data(**kwargs)

		user_email = self.kwargs.get('email', '')

		context['messages_viewed'] = self.n_viewed
		context['participant'] = get_object_or_404(User, email = user_email)
		context['talk_id'] = self.talk_id
		context['space'] = self.request.GET.get('space', '0')
		context['space_type'] = self.request.GET.get('space_type', 'general')
		context['form'] = ChatMessageForm()
		context['form_url'] = reverse_lazy('chat:create', args = (), kwargs = {'email': self.kwargs.get('email', ''), 'talk_id': self.talk_id, 'space': self.request.GET.get('space', '0'), 'space_type': self.request.GET.get('space_type', 'general')})

		if context['space_type'] == "subject":
			subject = get_object_or_404(Subject, id = context['space'])
			context['subject'] = subject.slug

		self.log_context['talk_id'] = self.talk_id
		self.log_context['user_id'] = context['participant'].id
		self.log_context['user_name'] = str(context['participant'])
		self.log_context['user_email'] = context['participant'].email

		super(GetTalk, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		return context

class SendMessage(LoginRequiredMixin, LogMixin, generic.edit.CreateView):
	log_component = "chat"
	log_action = "send"
	log_resource = "message"
	log_context = {}

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
			talk = Conversation.objects.create(user_one = self.request.user, user_two = user)			
		else:
			talk = get_object_or_404(Conversation, id = talk_id)

		self.object.talk = talk

		if space_type == 'subject':
			self.object.subject = get_object_or_404(Subject, id = space)
			space = self.object.subject.slug

		self.object.save()

		simple_notify = textwrap.shorten(strip_tags(self.object.text), width = 30, placeholder = "...")

		if self.object.image:
			simple_notify += " ".join(_("[Photo]"))
		
		notification = {
			"type": "chat",
			"subtype": space_type,
			"space": space,
			"user_icon": self.object.user.image_url,
			"notify_title": str(self.object.user),
			"simple_notify": simple_notify,
			"view_url": reverse("chat:view_message", args = (self.object.id, ), kwargs = {}),
			"complete": render_to_string("chat/_message.html", {"talk_msg": self.object}, self.request),
			"container": "chat-" + str(self.object.user.id),
			"last_date": _("Last message in %s")%(formats.date_format(self.object.create_date, "SHORT_DATETIME_FORMAT"))
		}

		notification = json.dumps(notification)

		Group("user-%s" % user.id).send({'text': notification})

		sendChatPushNotification(user, self.object)

		ChatVisualizations.objects.create(viewed = False, message = self.object, user = user)

		return super(SendMessage, self).form_valid(form)

	def get_context_data(self, **kwargs):
		context = super(SendMessage, self).get_context_data(**kwargs)

		context['form_url'] = reverse_lazy('chat:create', args = (), kwargs = {'email': self.kwargs.get('email', ''), 'talk_id': self.kwargs.get('talk_id', '-1'), 'space': self.kwargs.get('space', '0'), 'space_type': self.kwargs.get('space_type', 'general')})
		
		return context

	def get_success_url(self):
		user = get_object_or_404(User, email = self.kwargs.get('email', ''))

		self.log_context = {}

		self.log_context['talk_id'] = self.object.talk.id
		self.log_context['user_id'] = user.id
		self.log_context['user_name'] = str(user)
		self.log_context['user_email'] = user.email

		if self.object.subject:
			self.log_context['subject_id'] = self.object.subject.id
			self.log_context['subject_name'] = self.object.subject.name
			self.log_context['subject_slug'] = self.object.subject.slug

		super(SendMessage, self).createLog(self.request.user, self.log_component, self.log_action, self.log_resource, self.log_context)

		return reverse_lazy('chat:render_message', args = (self.object.id, self.object.talk.id, self.kwargs.get('space', '0'), self.kwargs.get('space_type', 'general'), self.kwargs.get('email', ''),))

def render_message(request, talk_msg, talk_id, space, space_type, email):
	msg = get_object_or_404(TalkMessages, id = talk_msg)

	context = {}
	context['talk_msg'] = msg
	
	form_url = reverse_lazy('chat:create', args = (), kwargs = {'email': email, 'talk_id': talk_id, 'space': space, 'space_type': space_type})
	loading_msg = reverse_lazy('chat:load_messages', args = (msg.talk.id, ))

	html = render_to_string("chat/_message.html", context, request)

	return JsonResponse({'view': html, 'new_id': msg.id, 'talk_id': msg.talk.id, 'new_form_url': form_url, 'load_msg_url': loading_msg})

@login_required
def favorite(request, message):
	action = request.GET.get('action', '')
	message = get_object_or_404(TalkMessages, id = message)

	if action == 'favorite':
		ChatFavorites.objects.create(message = message, user = request.user)

		return JsonResponse({'label': _('Unfavorite')})
	else:
		ChatFavorites.objects.filter(message = message, user = request.user).delete()

		return JsonResponse({'label': _('Favorite')})

def message_viewed(request, message):
	view = ChatVisualizations.objects.filter(message__id = message, user = request.user)

	view.update(viewed = True, date_viewed = datetime.now())

	return JsonResponse({'msg': 'ok'})

def load_messages(request, talk):
	context = {
		'request': request,
	}

	user = request.user
	favorites = request.GET.get('favorite', False)
	mines = request.GET.get('mine', False)
	showing = request.GET.get('showing', '')
	n_views = 0

	if not favorites:
		if mines:
			messages = TalkMessages.objects.filter(talk__id = talk, user = user)
		else:
			messages = TalkMessages.objects.filter(talk__id = talk)
	else:
		if mines:
			messages = TalkMessages.objects.filter(talk__id = talk, chat_favorites_message__isnull = False, chat_favorites_message__user = user, user = user)
		else:
			messages = TalkMessages.objects.filter(talk__id = talk, chat_favorites_message__isnull = False, chat_favorites_message__user = user)

	if showing: #Exclude ajax creation messages results
		showing = showing.split(',')
		messages = messages.exclude(id__in = showing)

	has_page = request.GET.get('page', None)

	paginator = Paginator(messages.order_by("-create_date"), 20)

	try:
		page_number = int(request.GET.get('page', 1))
	except ValueError:
		raise Http404

	try:
		page_obj = paginator.page(page_number)
	except EmptyPage:
		raise Http404

	context['messages'] = page_obj.object_list

	response = render_to_string("chat/_list_messages.html", context, request)

	return JsonResponse({"messages": response, "count": messages.count(), "num_pages": paginator.num_pages, "num_page": page_obj.number})