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

from channels import Group
import json

from categories.models import Category
from subjects.models import Subject
from users.models import User

from .models import Conversation, GeneralTalk, CategoryTalk, SubjectTalk, TalkMessages, ChatVisualizations, ChatFavorites
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

		conversations = Conversation.objects.filter((Q(user_one = user) | Q(user_two = user)) & Q(categorytalk__isnull = True) & Q(subjecttalk__isnull = True))
		
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
		context['search'] = self.request.GET.get('search', '')
		context['chat_menu_active'] = 'subjects_menu_active'
		
		return context

class CategoryIndex(LoginRequiredMixin, generic.ListView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'chat/list_category.html'
	context_object_name = "categories"
	paginate_by = 10

	totals = {}

	def get_queryset(self):
		user = self.request.user
		page = self.request.GET.get('page', False)

		if user.is_staff:
			categories = Category.objects.all()
		else:
			categories = Category.objects.filter(Q(coordinators__pk = user.pk) | Q(subject_category__professor__pk = user.pk) | Q(subject_category__students__pk = user.pk, visible = True)).distinct()
		
		self.totals['general'] = ChatVisualizations.objects.filter(user = user, viewed = False, message__talk__generaltalk__isnull = False).count()
		self.totals['category'] = ChatVisualizations.objects.filter(user = user, viewed = False, message__talk__categorytalk__isnull = False).count()
		self.totals['subject'] = ChatVisualizations.objects.filter(user = user, viewed = False, message__talk__subjecttalk__isnull = False).count()

		return categories

	def get_context_data(self, **kwargs):
		context = super(CategoryIndex, self).get_context_data(**kwargs)

		context['title'] = _('Messages per Category')
		context['totals'] = self.totals
		context['chat_menu_active'] = 'subjects_menu_active'
		
		return context

class CategoryTalks(LoginRequiredMixin, generic.ListView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'chat/_talks_list.html'
	context_object_name = "conversations"

	def get_queryset(self):
		user = self.request.user
		cat = self.kwargs.get('category', 0)

		conversations = CategoryTalk.objects.filter((Q(user_one = user) | Q(user_two = user)) & Q(space__id = cat))
		
		print(cat)

		return conversations

	def get_context_data(self, **kwargs):
		context = super(CategoryTalks, self).get_context_data(**kwargs)

		context['space'] = self.kwargs.get('category', 0)
		context['space_type'] = 'category'
		
		return context

class CategoryParticipants(LoginRequiredMixin, generic.ListView):
	login_url = reverse_lazy("users:login")
	redirect_field_name = 'next'

	template_name = 'chat/_participants.html'
	context_object_name = "participants"

	def get_queryset(self):
		user = self.request.user
		cat = self.kwargs.get('category', 0)
		search = self.request.GET.get('search', '')

		print(search)

		users = User.objects.filter((Q(username__icontains = search) | Q(last_name__icontains = search) | Q(social_name__icontains = search) | Q(email__icontains = search)) & (Q(is_staff = True) | Q(subject_student__category__id = cat) | Q(professors__category__id = cat) | Q(coordinators__id = cat))).distinct().order_by('social_name','username').exclude(email = user.email)
		
		return users

	def get_context_data(self, **kwargs):
		context = super(CategoryParticipants, self).get_context_data(**kwargs)

		context['space'] = self.kwargs.get('category', 0)
		context['space_type'] = 'category'
		
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

			views = ChatVisualizations.objects.filter(Q(user = user) & Q(viewed = False) & (Q(message__talk = talk)))
			views.update(viewed = True, date_viewed = datetime.now())

		return messages

	def get_context_data(self, **kwargs):
		context = super(GetTalk, self).get_context_data(**kwargs)

		user_email = self.kwargs.get('email', '')

		context['participant'] = get_object_or_404(User, email = user_email)
		context['talk_id'] = self.talk_id
		context['space'] = self.request.GET.get('space', '0')
		context['space_type'] = self.request.GET.get('space_type', 'general')
		context['form'] = ChatMessageForm()
		context['form_url'] = reverse_lazy('chat:create', args = (), kwargs = {'email': self.kwargs.get('email', ''), 'talk_id': self.talk_id, 'space': self.request.GET.get('space', '0'), 'space_type': self.request.GET.get('space_type', 'general')})

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

		subclass = self.object.talk._my_subclass

		if subclass == "generaltalk":
			space_type = "general"
		elif subclass == "categorytalk":
			space_type = "category"
			space = self.object.talk.categorytalk.space.slug
		else:
			space_type = "subject"
			space = self.object.talk.subjecttalk.space.slug

		notification = {
			"type": "chat",
			"subtype": space_type,
			"space": space,
			"user_icon": self.object.user.image_url,
			"notify_title": str(self.object.user),
			"simple_notify": simple_notify,
			"complete": render_to_string("chat/_message.html", {"talk_msg": self.object}, self.request),
			"container": "chat-" + str(self.object.user.id),
			"last_date": _("Last message in %s")%(formats.date_format(self.object.create_date, "SHORT_DATETIME_FORMAT"))
		}

		notification = json.dumps(notification)

		Group("user-%s" % user.id).send({'text': notification})

		ChatVisualizations.objects.create(viewed = False, message = self.object, user = user)

		return super(SendMessage, self).form_valid(form)

	def get_context_data(self, **kwargs):
		context = super(SendMessage, self).get_context_data(**kwargs)

		context['form_url'] = reverse_lazy('chat:create', args = (), kwargs = {'email': self.kwargs.get('email', ''), 'talk_id': self.kwargs.get('talk_id', '-1'), 'space': self.kwargs.get('space', '0'), 'space_type': self.kwargs.get('space_type', 'general')})
		
		return context

	def get_success_url(self):
		return reverse_lazy('chat:render_message', args = (self.object.id, self.object.talk.id, self.kwargs.get('space', '0'), self.kwargs.get('space_type', 'general'), self.kwargs.get('email', ''),))

def render_message(request, talk_msg, talk_id, space, space_type, email):
	msg = get_object_or_404(TalkMessages, id = talk_msg)

	context = {}
	context['talk_msg'] = msg
	
	form_url = reverse_lazy('chat:create', args = (), kwargs = {'email': email, 'talk_id': talk_id, 'space': space, 'space_type': space_type})

	html = render_to_string("chat/_message.html", context, request)

	return JsonResponse({'view': html, 'new_id': msg.id, 'talk_id': msg.talk.id, 'new_form_url': form_url})

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