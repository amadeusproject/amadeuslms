""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

import requests, json
from django.shortcuts import get_object_or_404, reverse
from django.contrib.auth import authenticate, logout as logout_user
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string
from django.db.models import Count
import textwrap
from datetime import datetime
from django.core import serializers
from django.utils import formats
from django.utils.html import strip_tags

from channels import Group

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    AllowAny,
)

from django.db.models import Q, TextField
from django.db.models.functions import Cast

from security.models import Security

from chat.serializers import ChatSerializer
from chat.models import TalkMessages, Conversation, ChatVisualizations, ChatFavorites

from log.models import Log
from log.mixins import LogMixin
from log.decorators import log_decorator

from subjects.serializers import SubjectSerializer
from subjects.models import Subject

from users.serializers import UserSerializer
from users.models import User

from mural.serializers import MuralSerializer, CommentsSerializer
from mural.models import SubjectPost, MuralVisualizations, Comment, MuralFavorites
from mural.utils import getSubjectPosts, getSpaceUsers

from notifications.models import Notification

from oauth2_provider.views.generic import ProtectedResourceView
from oauth2_provider.models import Application
from django.http import HttpResponse

from fcm_django.models import FCMDevice

from .utils import sendChatPushNotification, sendMuralPushNotification


@csrf_exempt
def getToken(request):
    oauth = Application.objects.filter(name="amadeus-droid")
    security = Security.objects.get(id=1)

    response = ""

    if request.method == "POST":
        json_data = json.loads(request.body.decode("utf-8"))

        try:
            username = json_data["email"]
            password = json_data["password"]

            user = authenticate(username=username, password=password)

            if user is not None:
                if not security.maintence or user.is_staff:
                    if oauth.count() > 0:
                        oauth = oauth[0]

                        data = {
                            "grant_type": "password",
                            "username": username,
                            "password": password,
                        }

                        auth = (oauth.client_id, oauth.client_secret)

                        """response = requests.post(
                            request.build_absolute_uri(
                                reverse("oauth2_provider:token")
                            ),
                            data=data,
                            auth=auth,
                        )
                        """

                        uri = request.build_absolute_uri(
                            reverse("oauth2_provider:token")
                        ).replace("http", "https")
                        response = requests.post(uri, data=data, auth=auth)

                        json_r = json.loads(response.content.decode("utf-8"))

                        json_r["message"] = ""
                        json_r["type"] = ""
                        json_r["title"] = ""
                        json_r["success"] = True
                        json_r["number"] = 1
                        json_r["extra"] = 0

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

    log_component = "mobile"
    log_action = "access"
    log_resource = "system"
    log_context = {}

    @csrf_exempt
    @action(detail=False, methods=["POST"], permission_classes=[AllowAny])
    def login(self, request):
        json_data = (
            request.data if request.data else json.loads(request.body.decode("utf-8"))
        )

        username = json_data["email"]

        user = self.queryset.filter(email=username).first()
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
            user_info["extra"] = 0

            response = json.dumps(user_info)

            super(LoginViewset, self).createLog(
                user,
                self.log_component,
                self.log_action,
                self.log_resource,
                self.log_context,
            )

        return HttpResponse(response)

    @csrf_exempt
    @action(detail=False, methods=["POST"], permission_classes=[IsAuthenticated])
    def register_device(self, request):
        json_data = (
            request.data if request.data else json.loads(request.body.decode("utf-8"))
        )

        username = json_data["email"]
        device = json_data["device"]

        user = self.queryset.get(email=username)
        response = ""
        json_r = {}

        if not user is None:
            fcm_d = FCMDevice()
            fcm_d.name = "phone"
            fcm_d.registration_id = device
            fcm_d.type = "android"
            fcm_d.user = user

            fcm_d.save()

            if not fcm_d.pk is None:
                FCMDevice.objects.filter(registration_id=device).exclude(
                    pk=fcm_d.pk
                ).update(active=False)

                json_r["message"] = ""
                json_r["type"] = ""
                json_r["title"] = ""
                json_r["success"] = True
                json_r["number"] = 1
                json_r["extra"] = 0

            response = json.dumps(json_r)

        return HttpResponse(response)

    @csrf_exempt
    @action(detail=False, methods=["POST"], permission_classes=[IsAuthenticated])
    def logout(self, request):
        json_data = (
            request.data if request.data else json.loads(request.body.decode("utf-8"))
        )

        username = json_data["email"]
        device = json_data["device"]

        user = self.queryset.get(email=username)
        response = ""
        json_r = {}

        if not user is None:
            FCMDevice.objects.filter(
                registration_id=device, user__email=username
            ).delete()

            logout_user(request)

            json_r["message"] = ""
            json_r["type"] = ""
            json_r["title"] = ""
            json_r["success"] = True
            json_r["number"] = 1
            json_r["extra"] = 0

            response = json.dumps(json_r)

            self.log_action = "logout"

            super(LoginViewset, self).createLog(
                user,
                self.log_component,
                self.log_action,
                self.log_resource,
                self.log_context,
            )

        return HttpResponse(response)


class SubjectViewset(viewsets.ReadOnlyModelViewSet):
    """
    ---
    get_subjects:
        Get list of subjects of a user.	Require user email as parameter
    """

    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

    @csrf_exempt
    @action(detail=False, methods=["POST"], permission_classes=[IsAuthenticated])
    def get_subjects(self, request):
        json_data = (
            request.data if request.data else json.loads(request.body.decode("utf-8"))
        )

        username = json_data["email"]

        user = User.objects.get(email=username)

        subjects = None

        response = ""

        if not user is None:
            if user.is_staff:
                subjects = Subject.objects.all().order_by("name")
            else:
                pk = user.pk

                subjects = Subject.objects.filter(
                    Q(students__pk=pk)
                    | Q(professor__pk=pk)
                    | Q(category__coordinators__pk=pk)
                ).distinct()

            serializer = SubjectSerializer(
                subjects, many=True, context={"request_user": user}
            )

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
            sub_info["extra"] = 0

            response = json.dumps(sub_info)

        return HttpResponse(response)


class ParticipantsViewset(viewsets.ReadOnlyModelViewSet, LogMixin):
    """
    get_participants:
        Get all users that participates in some subject. Require the logged user email and the subject slug
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer

    log_component = "mobile"
    log_action = "view"
    log_resource = "subject_participants"
    log_context = {}

    @csrf_exempt
    @action(detail=False, methods=["POST"], permission_classes=[IsAuthenticated])
    def get_participants(self, request):
        json_data = (
            request.data if request.data else json.loads(request.body.decode("utf-8"))
        )

        username = json_data["email"]
        subject_slug = json_data["subject_slug"]

        user = User.objects.get(email=username)

        participants = None

        response = ""

        if not subject_slug == "":
            subject = Subject.objects.get(slug=subject_slug)

            participants = (
                User.objects.filter(
                    Q(subject_student__slug=subject_slug)
                    | Q(professors__slug=subject_slug)
                    | Q(coordinators__subject_category__slug=subject_slug)
                )
                .exclude(email=username)
                .distinct()
            )

            serializer = UserSerializer(
                participants, many=True, context={"request_user": username}
            )

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
            info["extra"] = 0

            response = json.dumps(info)

            self.log_context["subject_id"] = subject.id
            self.log_context["subject_slug"] = subject_slug
            self.log_context["subject_name"] = subject.name

            super(ParticipantsViewset, self).createLog(
                user,
                self.log_component,
                self.log_action,
                self.log_resource,
                self.log_context,
            )

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

    log_component = "mobile"
    log_action = "view"
    log_resource = "talk"
    log_context = {}

    @csrf_exempt
    @action(detail=False, methods=["POST"], permission_classes=[IsAuthenticated])
    def get_messages(self, request):
        json_data = (
            request.data if request.data else json.loads(request.body.decode("utf-8"))
        )

        username = json_data["email"]
        user_two = json_data["user_two"]
        n_page = int(json_data["page"])
        messages_by_page = int(json_data["page_size"])

        user = User.objects.get(email=username)

        messages = None

        response = ""

        if not user_two == "":
            user2 = User.objects.get(email=user_two)

            messages = TalkMessages.objects.filter(
                (Q(talk__user_one__email=username) & Q(talk__user_two__email=user_two))
                | (
                    Q(talk__user_one__email=user_two)
                    & Q(talk__user_two__email=username)
                )
            ).order_by("-create_date")

            views = ChatVisualizations.objects.filter(
                Q(user=user)
                & (
                    Q(message__talk__user_two__email=user_two)
                    | Q(message__talk__user_one__email=user_two)
                )
                & Q(viewed=False)
            )

            views.update(viewed=True, date_viewed=datetime.now())

            page = []

            for i in range(
                messages_by_page * (n_page - 1), (n_page * messages_by_page)
            ):
                if i >= messages.count():
                    break
                else:
                    page.append(messages[i])

            serializer = ChatSerializer(page, many=True, context={"request_user": user})

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
            info["extra"] = 0

            response = json.dumps(info)

            try:
                talk = Conversation.objects.get(
                    (Q(user_one__email=username) & Q(user_two__email=user_two))
                    | (Q(user_two__email=username) & Q(user_one__email=user_two))
                )
                self.log_context["talk_id"] = talk.id
            except Conversation.DoesNotExist:
                pass

            self.log_context["user_id"] = user2.id
            self.log_context["user_name"] = str(user2)
            self.log_context["user_email"] = user_two

            super(ChatViewset, self).createLog(
                user,
                self.log_component,
                self.log_action,
                self.log_resource,
                self.log_context,
            )

        return HttpResponse(response)

    @csrf_exempt
    @action(detail=False, methods=["POST"], permission_classes=[IsAuthenticated])
    def send_message(self, request):
        self.log_action = "send"
        self.log_resource = "message"
        self.log_context = {}

        if "file" in request.data:
            file = request.FILES["file"]

            data = json.loads(request.data["data"])

            username = data["email"]
            user_two = data["user_two"]
            subject = data["subject"]
            msg_text = data["text"]
            create_date = data["create_date"]
        else:
            file = None
            data = (
                request.data
                if request.data
                else json.loads(request.body.decode("utf-8"))
            )
            username = data["email"]
            user_two = data["user_two"]
            subject = data["subject"]
            msg_text = data["text"]
            create_date = data["create_date"]

        info = {}

        if not user_two == "" and not username == "":
            user = User.objects.get(email=username)
            user_to = User.objects.get(email=user_two)

            talks = Conversation.objects.filter(
                (Q(user_one__email=username) & Q(user_two__email=user_two))
                | (Q(user_two__email=username) & Q(user_one__email=user_two))
            )

            if talks.count() > 0:
                talk = talks[0]
            else:
                talk = Conversation()
                talk.user_one = user
                talk.user_two = user_to

                talk.save()

            if subject != "":
                subject = Subject.objects.get(slug=subject)
                space = subject.slug
                space_type = "subject"

                self.log_context["subject_id"] = subject.id
                self.log_context["subject_slug"] = space
                self.log_context["subject_name"] = subject.name
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

            self.log_context["talk_id"] = talk.id
            self.log_context["user_id"] = user_to.id
            self.log_context["user_name"] = str(user_to)
            self.log_context["user_email"] = user_two

            if not message.pk is None:
                simple_notify = textwrap.shorten(
                    strip_tags(message.text), width=30, placeholder="..."
                )

                notification = {
                    "type": "chat",
                    "subtype": space_type,
                    "space": space,
                    "user_icon": message.user.image_url,
                    "notify_title": str(message.user),
                    "simple_notify": simple_notify,
                    "view_url": reverse(
                        "chat:view_message", args=(message.id,), kwargs={}
                    ),
                    "complete": render_to_string(
                        "chat/_message.html", {"talk_msg": message}, request
                    ),
                    "container": "chat-" + str(message.user.id),
                    "last_date": _("Last message in %s")
                    % (
                        formats.date_format(
                            message.create_date, "SHORT_DATETIME_FORMAT"
                        )
                    ),
                }

                notification = json.dumps(notification)

                Group("user-%s" % user_to.id).send({"text": notification})

                ChatVisualizations.objects.create(
                    viewed=False, message=message, user=user_to
                )

                serializer = ChatSerializer(message)

                json_r = json.dumps(serializer.data)
                json_r = json.loads(json_r)

                info["data"] = {}
                info["data"]["message_sent"] = json_r

                info["message"] = _("Message sent successfully!")
                info["success"] = True
                info["number"] = 1

                sendChatPushNotification(user_to, message)

                super(ChatViewset, self).createLog(
                    user,
                    self.log_component,
                    self.log_action,
                    self.log_resource,
                    self.log_context,
                )
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
        info["extra"] = 0

        response = json.dumps(info)

        return HttpResponse(response)

    @csrf_exempt
    @action(detail=False, methods=["POST"], permission_classes=[IsAuthenticated])
    def favorite_messages(self, request):
        json_data = (
            request.data if request.data else json.loads(request.body.decode("utf-8"))
        )

        username = json_data["email"]
        favor = json_data["favor"]
        list_size = int(json_data["list_size"])

        user = User.objects.get(email=username)

        entries = []
        array_ids = []

        for i in range(0, list_size):

            message_id = int(json_data[str(i)])

            message = get_object_or_404(TalkMessages, id=message_id)

            if favor == "true":
                if not ChatFavorites.objects.filter(
                    Q(user=user) & Q(message__id=message_id)
                ).exists():
                    entries.append(ChatFavorites(message=message, user=user))
            elif favor == "false":
                if ChatFavorites.objects.filter(
                    Q(user=user) & Q(message__id=message_id)
                ).exists():
                    array_ids.append(message_id)

        if favor == "true":
            ChatFavorites.objects.bulk_create(entries)
        elif favor == "false":
            ChatFavorites.objects.filter(message__id__in=(array_ids)).delete()

        response = ""

        info = {}

        info["message"] = ""
        info["type"] = ""
        info["title"] = ""
        info["success"] = True
        info["number"] = 1
        info["extra"] = 0

        response = json.dumps(info)

        return HttpResponse(response)


class MuralViewset(viewsets.ModelViewSet, LogMixin):
    queryset = SubjectPost.objects.all()
    serializer_class = MuralSerializer

    log_component = "mobile"
    log_action = "view"
    log_resource = "mural"
    log_context = {}

    @csrf_exempt
    @action(detail=False, methods=["POST"], permission_classes=[IsAuthenticated])
    def get_posts(self, request):
        json_data = (
            request.data if request.data else json.loads(request.body.decode("utf-8"))
        )

        username = json_data["email"]
        subject = json_data["subject"]
        favorites = json_data["only_fav"]
        mines = json_data["only_mine"]
        n_page = int(json_data["page"])
        posts_by_page = int(json_data["page_size"])

        user = User.objects.get(email=username)
        sub = Subject.objects.get(slug=subject)

        posts = getSubjectPosts(sub.id, user, favorites == "True", mines == "True")
        posts = posts.order_by("-most_recent")

        page = []

        response = ""

        if n_page is None or n_page == 0:
            views = MuralVisualizations.objects.filter(
                Q(user=user)
                & Q(viewed=False)
                & (
                    Q(comment__post__subjectpost__space__id=sub.id)
                    | Q(post__subjectpost__space__id=sub.id)
                )
            )
            views.update(viewed=True, date_viewed=datetime.now())

        for i in range(posts_by_page * n_page, ((n_page + 1) * posts_by_page)):
            if i >= posts.count():
                break
            else:
                page.append(posts[i])

        serializer = MuralSerializer(
            page, many=True, context={"request_user": user, "subject": subject}
        )

        json_r = json.dumps(serializer.data)
        json_r = json.loads(json_r)

        info = {}

        info["data"] = {}
        info["data"]["posts"] = json_r

        info["message"] = ""
        info["type"] = ""
        info["title"] = ""
        info["success"] = True
        info["number"] = 1
        info["extra"] = 0

        response = json.dumps(info)

        self.log_context["subject_id"] = sub.id
        self.log_context["subject_slug"] = subject
        self.log_context["subject_name"] = sub.name

        super(MuralViewset, self).createLog(
            user,
            self.log_component,
            self.log_action,
            self.log_resource,
            self.log_context,
        )

        return HttpResponse(response)

    @csrf_exempt
    @action(detail=False, methods=["POST"], permission_classes=[IsAuthenticated])
    def get_comments(self, request):
        json_data = (
            request.data if request.data else json.loads(request.body.decode("utf-8"))
        )

        post_id = json_data["post_id"]
        n_page = int(json_data["page"])
        comments_by_page = int(json_data["page_size"])

        mural = SubjectPost.objects.get(id=post_id)

        page = []

        comments = Comment.objects.filter(post__id=post_id).order_by("-last_update")

        for i in range(comments_by_page * n_page, ((n_page + 1) * comments_by_page)):
            if i >= comments.count():
                break
            else:
                page.append(comments[i])

        serializer = CommentsSerializer(
            page,
            many=True,
            context={"request_user": mural.user, "subject": mural.space.slug},
        )

        json_r = json.dumps(serializer.data)
        json_r = json.loads(json_r)

        info = {}

        info["data"] = {}
        info["data"]["comments"] = json_r

        info["message"] = ""
        info["type"] = ""
        info["title"] = ""
        info["success"] = True
        info["number"] = 1
        info["extra"] = 0

        response = json.dumps(info)

        self.log_resource = "post_comments"
        self.log_context["post_id"] = mural.id
        self.log_context["post_space_id"] = mural.space.id
        self.log_context["post_space_slug"] = mural.space.slug
        self.log_context["post_space_name"] = mural.space.name

        super(MuralViewset, self).createLog(
            mural.user,
            self.log_component,
            self.log_action,
            self.log_resource,
            self.log_context,
        )

        return HttpResponse(response)

    @csrf_exempt
    @action(detail=False, methods=["POST"], permission_classes=[IsAuthenticated])
    def create_post(self, request):
        self.log_action = "send"
        self.log_resource = "mural"
        self.log_context = {}

        if "file" in request.data:
            file = request.FILES["file"]

            data = json.loads(request.data["data"])
        else:
            file = None

            data = (
                request.data
                if request.data
                else json.loads(request.body.decode("utf-8"))
            )

        username = data["email"]
        message = data["message"]
        space = data["subject"]
        action = data["action"]

        info = {}

        subject = Subject.objects.get(slug=space)
        user = User.objects.get(email=username)

        post = SubjectPost()
        post.action = action
        post.space = subject
        post.post = message
        post.user = user

        if not file is None:
            post.image = file

        post.save()

        if not post.pk is None:
            users = getSpaceUsers(user.id, post)

            entries = []

            paths = [
                reverse("mural:manage_subject"),
                reverse("mural:subject_view", args=(), kwargs={"slug": subject.slug}),
            ]

            simple_notify = _("%s has made a post in %s") % (
                str(post.user),
                str(post.space),
            )

            notification = {
                "type": "mural",
                "subtype": "post",
                "paths": paths,
                "user_icon": user.image_url,
                "simple_notify": simple_notify,
                "complete": render_to_string(
                    "mural/_view.html", {"post": post}, request
                ),
                "container": "#" + subject.slug,
                "accordion": True,
                "post_type": "subjects",
            }

            notification = json.dumps(notification)

            for user in users:
                entries.append(MuralVisualizations(viewed=False, user=user, post=post))
                sendMuralPushNotification(user, post.user, simple_notify)
                Group("user-%s" % user.id).send({"text": notification})

            MuralVisualizations.objects.bulk_create(entries)

            self.log_context["subject_id"] = post.space.id
            self.log_context["subject_name"] = post.space.name
            self.log_context["subject_slug"] = post.space.slug

            serializer = MuralSerializer(
                post, context={"request_user": user, "subject": space}
            )

            json_r = json.dumps(serializer.data)
            json_r = json.loads(json_r)

            info["data"] = {}
            info["data"]["new_post"] = json_r

            info["message"] = _("Post created successfully!")
            info["success"] = True
            info["number"] = 1

            super(MuralViewset, self).createLog(
                user,
                self.log_component,
                self.log_action,
                self.log_resource,
                self.log_context,
            )
        else:
            info["message"] = _("Error while creating post!")
            info["success"] = False
            info["number"] = 0

        response = json.dumps(info)

        return HttpResponse(response)

    @csrf_exempt
    @action(detail=False, methods=["POST"], permission_classes=[IsAuthenticated])
    def create_comment(self, request):
        self.log_action = "send"
        self.log_resource = "post_comment"
        self.log_context = {}

        if "file" in request.data:
            file = request.FILES["file"]

            data = json.loads(request.data["data"])
        else:
            file = None

            data = (
                request.data
                if request.data
                else json.loads(request.body.decode("utf-8"))
            )

        username = data["email"]
        message = data["message"]
        post = data["post_id"]

        info = {}

        mural = SubjectPost.objects.get(id=post)
        user = User.objects.get(email=username)

        comment = Comment()
        comment.comment = message
        comment.post = mural
        comment.user = user

        if not file is None:
            comment.image = file

        comment.save()

        if not comment.pk is None:
            users = getSpaceUsers(user.id, mural)

            entries = []

            paths = [
                reverse("mural:manage_general"),
                reverse("mural:manage_category"),
                reverse("mural:manage_subject"),
                reverse(
                    "mural:subject_view",
                    args=(),
                    kwargs={"slug": mural.get_space_slug()},
                ),
            ]

            simple_notify = _("%s has commented in a post") % (str(comment.user))

            notification = {
                "type": "mural",
                "subtype": "post",
                "paths": paths,
                "user_icon": user.image_url,
                "simple_notify": simple_notify,
                "complete": render_to_string(
                    "mural/_view_comment.html", {"comment": comment}, request
                ),
                "container": "#post-" + str(mural.get_id()),
                "post_type": mural._my_subclass,
                "type_slug": mural.get_space_slug(),
            }

            notification = json.dumps(notification)

            for user in users:
                entries.append(
                    MuralVisualizations(viewed=False, user=user, comment=comment)
                )
                sendMuralPushNotification(user, comment.user, simple_notify)
                Group("user-%s" % user.id).send({"text": notification})

            MuralVisualizations.objects.bulk_create(entries)

            self.log_context["post_id"] = mural.id
            self.log_context["subject_id"] = mural.space.id
            self.log_context["subject_name"] = mural.space.name
            self.log_context["subject_slug"] = mural.space.slug

            serializer = CommentsSerializer(
                comment, context={"request_user": user, "subject": mural.space.slug}
            )

            json_r = json.dumps(serializer.data)
            json_r = json.loads(json_r)

            info["data"] = {}
            info["data"]["new_comment"] = json_r

            info["message"] = _("Comment created successfully!")
            info["success"] = True
            info["number"] = 1

            super(MuralViewset, self).createLog(
                user,
                self.log_component,
                self.log_action,
                self.log_resource,
                self.log_context,
            )
        else:
            info["message"] = _("Error while creating comment!")
            info["success"] = False
            info["number"] = 0

        response = json.dumps(info)

        return HttpResponse(response)

    @csrf_exempt
    @action(detail=False, methods=["POST"], permission_classes=[IsAuthenticated])
    def favorite(self, request):
        json_data = (
            request.data if request.data else json.loads(request.body.decode("utf-8"))
        )

        username = json_data["email"]
        favor = json_data["favor"]
        post = json_data["post_id"]

        user = User.objects.get(email=username)
        mural = SubjectPost.objects.get(id=post)

        if favor == "true":
            MuralFavorites.objects.create(post=mural, user=user)
        else:
            MuralFavorites.objects.filter(post=mural, user=user).delete()

        response = ""

        info = {}

        info["message"] = ""
        info["type"] = ""
        info["title"] = ""
        info["success"] = True
        info["number"] = 1
        info["extra"] = 0

        response = json.dumps(info)

        return HttpResponse(response)


@csrf_exempt
@log_decorator("mobile", "view", "subject_pendencies")
def getPendencies(request):
    response = ""

    json_r = {}

    if request.method == "POST":
        json_data = json.loads(request.body.decode("utf-8"))

        try:
            username = json_data["email"]
            subject = json_data["subject_slug"]

            if username is not None and subject is not None:
                notifications = (
                    Notification.objects.filter(
                        user__email=username,
                        task__resource__topic__subject__slug=subject,
                    )
                    .annotate(str_date=Cast("creation_date", TextField()))
                    .values("str_date")
                    .order_by("-str_date")
                    .annotate(total=Count("str_date"))
                )

                json_r["data"] = list(notifications)

                json_r["message"] = ""
                json_r["type"] = ""
                json_r["title"] = ""
                json_r["success"] = True
                json_r["number"] = 1
                json_r["extra"] = 0

                response = json.dumps(json_r)

                subject = Subject.objects.get(slug=subject)

                request.log_context = {}
                request.log_context["subject_id"] = subject.id
                request.log_context["subject_slug"] = subject.slug
                request.log_context["subject_name"] = subject.name

        except KeyError:
            response = "Error"

    return HttpResponse(response)
