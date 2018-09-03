""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

import requests, json
from django.shortcuts import get_object_or_404, reverse
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string
import textwrap
from datetime import datetime
from django.utils import formats
from django.utils.html import strip_tags

from channels import Group

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from django.db.models import Q

from security.models import Security

from chat.serializers import ChatSerializer
from chat.models import TalkMessages, Conversation, ChatVisualizations, ChatFavorites

from log.models import Log
from log.mixins import LogMixin

from subjects.serializers import SubjectSerializer
from subjects.models import Subject

from users.serializers import UserSerializer
from users.models import User

from oauth2_provider.views.generic import ProtectedResourceView
from oauth2_provider.models import Application
from django.http import HttpResponse

from fcm_django.models import FCMDevice

from .utils import  sendChatPushNotification

@csrf_exempt
def getToken(request):
	oauth = Application.objects.filter(name = "amadeus-droid")
	security = Security.objects.get(id = 1)

	response = ""

	if request.method == "POST":
		json_data = json.loads(request.body.decode('utf-8'))

		try:
			username = json_data['email']
			password = json_data['password']

			user = authenticate(username = username, password = password)

			if user is not None:
				if not security.maintence or user.is_staff:
					if oauth.count() > 0:
						oauth = oauth[0]

						data = {
							"grant_type": "password",
							"username": username,
							"password": password
						}

						auth = (oauth.client_id, oauth.client_secret)
						
						response = requests.post(request.build_absolute_uri(reverse('oauth2_provider:token')), data = data, auth = auth)

						json_r = json.loads(response.content.decode('utf-8'))

						json_r["message"] = ""
						json_r["type"] = ""
						json_r["title"] = ""
						json_r["success"] = True
						json_r["number"] = 1
						json_r['extra'] = 0

						response = json.dumps(json_r)
		except KeyError:
			response = "Error"
		
	return HttpResponse(response)

class LoginViewset(viewsets.ReadOnlyModelViewSet, LogMixin):
	"""
	login:
	Log a user in the system

	register_device:
	Register a mobile device for the logged user to provide app notifications
	"""

	queryset = User.objects.all()
	serializer_class = UserSerializer
	permissions_classes = (IsAuthenticated,)

	log_component = 'mobile'
	log_action = 'access'
	log_resource = 'system'
	log_context = {}

	@csrf_exempt
	@list_route(methods = ['POST'], permissions_classes = [IsAuthenticated])
	def login(self, request):
		username = request.data['email']
		
		user = self.queryset.get(email = username)
		response = ""

		if not user is None:
			serializer = UserSerializer(user)

			json_r = json.dumps(serializer.data)
			json_r = json.loads(json_r)
			
			user_info = {}
			user_info["data"] = json_r

			user_info["message"] = ""
			user_info["type"] = ""
			user_info["title"] = ""
			user_info["success"] = True
			user_info["number"] = 1
			user_info['extra'] = 0

			response = json.dumps(user_info)
			
			super(LoginViewset, self).createLog(user, self.log_component, self.log_action, self.log_resource, self.log_context)

		return HttpResponse(response)

	@csrf_exempt
	@list_route(methods = ['POST'], permissions_classes = [IsAuthenticated])
	def register_device(self, request):
		username = request.data['email']
		device = request.data['device']
		
		user = self.queryset.get(email = username)
		response = ""
		json_r = {}

		if not user is None:
			fcm_d = FCMDevice()
			fcm_d.name = "phone" 
			fcm_d.registration_id = device
			fcm_d.type = 'android'
			fcm_d.user = user

			fcm_d.save()

			if not fcm_d.pk is None:
				FCMDevice.objects.filter(registration_id = device).exclude(pk = fcm_d.pk).update(active = False)

				json_r["message"] = ""
				json_r["type"] = ""
				json_r["title"] = ""
				json_r["success"] = True
				json_r["number"] = 1
				json_r['extra'] = 0

			response = json.dumps(json_r)
					
		return HttpResponse(response)

class SubjectViewset(viewsets.ReadOnlyModelViewSet):
	"""
	---
	get_subjects:
		Get list of subjects of a user.	Require user email as parameter
	"""

	queryset = Subject.objects.all()
	serializer_class = SubjectSerializer
	permissions_classes = (IsAuthenticated,)

	@csrf_exempt
	@list_route(methods = ['POST'], permissions_classes = [IsAuthenticated])
	def get_subjects(self, request):
		username = request.data['email']

		user = User.objects.get(email = username)

		subjects = None

		response = ""

		if not user is None:
			if user.is_staff:
				subjects = Subject.objects.all().order_by("name")
			else:
				pk = user.pk

				subjects = Subject.objects.filter(Q(students__pk=pk) | Q(professor__pk=pk) | Q(category__coordinators__pk=pk)).distinct()

			serializer = SubjectSerializer(subjects, many = True, context = {"request_user": user})

			json_r = json.dumps(serializer.data)
			json_r = json.loads(json_r)
			
			sub_info = {}

			sub_info["data"] = {}
			sub_info["data"]["subjects"] = json_r

			sub_info["message"] = ""
			sub_info["type"] = ""
			sub_info["title"] = ""
			sub_info["success"] = True
			sub_info["number"] = 1
			sub_info['extra'] = 0

			response = json.dumps(sub_info)

		return HttpResponse(response)

class ParticipantsViewset(viewsets.ReadOnlyModelViewSet, LogMixin):
	"""
	get_participants:
		Get all users that participates in some subject. Require the logged user email and the subject slug
	"""

	queryset = User.objects.all()
	serializer_class = UserSerializer
	permissions_classes = (IsAuthenticated, )

	log_component = 'mobile'
	log_action = 'view'
	log_resource = 'subject_participants'
	log_context = {}

	@csrf_exempt
	@list_route(methods = ['POST'], permissions_classes = [IsAuthenticated])
	def get_participants(self, request):
		username = request.data['email']
		subject_slug = request.data['subject_slug']

		user = User.objects.get(email = username)

		participants = None

		response = ""

		if not subject_slug == "":
			subject = Subject.objects.get(slug = subject_slug)

			participants = User.objects.filter(Q(is_staff = True) | Q(subject_student__slug = subject_slug) | Q(professors__slug = subject_slug) | Q(coordinators__subject_category__slug = subject_slug)).exclude(email = username).distinct()

			serializer = UserSerializer(participants, many = True, context = {"request_user": username})

			json_r = json.dumps(serializer.data)
			json_r = json.loads(json_r)
			
			info = {}

			info["data"] = {}
			info["data"]["participants"] = json_r

			info["message"] = ""
			info["type"] = ""
			info["title"] = ""
			info["success"] = True
			info["number"] = 1
			info['extra'] = 0

			response = json.dumps(info)

			self.log_context['subject_id'] = subject.id
			self.log_context['subject_slug'] = subject_slug
			self.log_context['subject_name'] = subject.name

			super(ParticipantsViewset, self).createLog(user, self.log_component, self.log_action, self.log_resource, self.log_context)

		return HttpResponse(response)

class ChatViewset(viewsets.ModelViewSet, LogMixin):
	"""
	get_messages:
		Get messages of a conversation

	send_message:
		Send a message in a conversation
	"""

	queryset = TalkMessages.objects.all()
	serializer_class = ChatSerializer
	permissions_classes = (IsAuthenticated, )

	log_component = 'mobile'
	log_action = 'view'
	log_resource = 'talk'
	log_context = {}

	@csrf_exempt
	@list_route(methods = ['POST'], permissions_classes = [IsAuthenticated])
	def get_messages(self, request):
		username = request.data['email']
		user_two = request.data['user_two']
		n_page = int(request.data['page'])
		messages_by_page = int(request.data['page_size'])
		#messages_by_page = 15

		user = User.objects.get(email = username)

		messages = None

		response = ""

		if not user_two == "":
			user2 = User.objects.get(email = user_two)

			messages = TalkMessages.objects.filter((Q(talk__user_one__email = username) & Q(talk__user_two__email = user_two)) | (Q(talk__user_one__email = user_two) & Q(talk__user_two__email = username))).order_by('-create_date')

			ChatVisualizations.objects.filter(Q(user = user) & Q(message__talk__user_two__email = user_two) & Q(viewed = False)).update(viewed = True)

			page = []

			for i in range(messages_by_page*(n_page - 1), (n_page*messages_by_page)):
				if i >= messages.count():
					break;
				else:
					page.append(messages[i])

			serializer = ChatSerializer(page, many = True, context = {"request_user": user})

			json_r = json.dumps(serializer.data)
			json_r = json.loads(json_r)
			
			info = {}

			info["data"] = {}
			info["data"]["messages"] = json_r
			info["data"]["message_sent"] = {}

			info["message"] = ""
			info["type"] = ""
			info["title"] = ""
			info["success"] = True
			info["number"] = 1
			info['extra'] = 0

			response = json.dumps(info)

			try:
				talk = Conversation.objects.get((Q(user_one__email = username) & Q(user_two__email = user_two)) | (Q(user_two__email = username) & Q(user_one__email = user_two)))
				self.log_context['talk_id'] = talk.id
			except Conversation.DoesNotExist:
				pass
			
			self.log_context['user_id'] = user2.id
			self.log_context['user_name'] = str(user2)
			self.log_context['user_email'] = user_two

			super(ChatViewset, self).createLog(user, self.log_component, self.log_action, self.log_resource, self.log_context)

		return HttpResponse(response)

	@csrf_exempt
	@list_route(methods = ['POST'], permissions_classes = [IsAuthenticated])
	def send_message(self, request):
		self.log_action = 'send'
		self.log_resource = 'message'
		self.log_context = {}

		if 'file' in request.data:
			file = request.FILES['file']
			
			data = json.loads(request.data['data'])

			username = data['email']
			user_two = data['user_two']
			subject = data['subject']
			msg_text = data['text']
			create_date = data['create_date']
		else:
			file = None
			username = request.data['email']
			user_two = request.data['user_two']
			subject = request.data['subject']
			msg_text = request.data['text']
			create_date = request.data['create_date']

		info = {}

		if not user_two == "" and not username == "":
			user = User.objects.get(email = username)
			user_to = User.objects.get(email = user_two)

			talks = Conversation.objects.filter((Q(user_one__email = username) & Q(user_two__email = user_two)) | (Q(user_two__email = username) & Q(user_one__email = user_two)))

			if talks.count() > 0:
				talk = talks[0]
			else:
				talk = Conversation()
				talk.user_one = user
				talk.user_two = user_to

				talk.save()

			if subject != "":
				subject = Subject.objects.get(slug = subject)
				space = subject.slug
				space_type = "subject"

				self.log_context['subject_id'] = subject.id
				self.log_context['subject_slug'] = space
				self.log_context['subject_name'] = subject.name
			else: 
				subject = None
				space = 0
				space_type = "general"

			message = TalkMessages()
			message.text = "<p>" + msg_text + "</p>"
			message.user = user
			message.talk = talk
			message.subject = subject

			if not file is None:
				message.image = file

			message.save()

			self.log_context['talk_id'] = talk.id
			self.log_context['user_id'] = user_to.id
			self.log_context['user_name'] = str(user_to)
			self.log_context['user_email'] = user_two

			if not message.pk is None:
				simple_notify = textwrap.shorten(strip_tags(message.text), width = 30, placeholder = "...")

				notification = {
					"type": "chat",
					"subtype": space_type,
					"space": space,
					"user_icon": message.user.image_url,
					"notify_title": str(message.user),
					"simple_notify": simple_notify,
					"view_url": reverse("chat:view_message", args = (message.id, ), kwargs = {}),
					"complete": render_to_string("chat/_message.html", {"talk_msg": message}, request),
					"container": "chat-" + str(message.user.id),
					"last_date": _("Last message in %s")%(formats.date_format(message.create_date, "SHORT_DATETIME_FORMAT"))
				}

				notification = json.dumps(notification)

				Group("user-%s" % user_to.id).send({'text': notification})

				ChatVisualizations.objects.create(viewed = False, message = message, user = user_to)

				serializer = ChatSerializer(message)

				json_r = json.dumps(serializer.data)
				json_r = json.loads(json_r)

				info["data"] = {}
				info["data"]["message_sent"] = json_r

				info["message"] = _("Message sent successfully!")
				info["success"] = True
				info["number"] = 1

				sendChatPushNotification(user_to, message)

				super(ChatViewset, self).createLog(user, self.log_component, self.log_action, self.log_resource, self.log_context)
			else:
				info["message"] = _("Error while sending message!")
				info["success"] = False
				info["number"] = 0
		else:
			info["data"] = {}
			info["data"]["message_sent"] = {}

			info["message"] = _("No information received!")
			info["success"] = False
			info["number"] = 0

		info["data"]["messages"] = []
		info["type"] = ""
		info["title"] = _("Amadeus")
		info['extra'] = 0

		response = json.dumps(info)

		return HttpResponse(response)

	@csrf_exempt
	@list_route(methods = ['POST'], permissions_classes = [IsAuthenticated])
	def favorite_messages(self, request):
		username = request.data['email']
		favor = request.data['favor']
		list_size = int(request.data['list_size'])

		user = User.objects.get(email = username)

		entries = []
		array_ids = []

		for i in range(0, list_size):

			message_id = int(request.data[str(i)])

			message = get_object_or_404(TalkMessages, id = message_id)

			if favor == "true":
				if not ChatFavorites.objects.filter(Q(user = user) & Q(message__id = message_id)).exists():
					entries.append(ChatFavorites(message = message, user = user))
			elif favor == "false":
				if ChatFavorites.objects.filter(Q(user = user) & Q(message__id = message_id)).exists():
					array_ids.append(message_id)

		if favor == "true":
			ChatFavorites.objects.bulk_create(entries)
		elif favor == "false":
			ChatFavorites.objects.filter(message__id__in = (array_ids)).delete()
		
		response = ""

		info = {}

		info["message"] = ""
		info["type"] = ""
		info["title"] = ""
		info["success"] = True
		info["number"] = 1
		info['extra'] = 0

		response = json.dumps(info)

		return HttpResponse(response)