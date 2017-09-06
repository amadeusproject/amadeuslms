import json
import textwrap
from django.db.models import Q
from django.utils import timezone
from django.utils import formats
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from channels import Group

from api.utils import sendChatPushNotification

from chat.models import Conversation, TalkMessages, ChatVisualizations
from users.models import User

from .models import GoalItem, MyGoals

def set_goals():
	specifications = GoalItem.objects.filter(goal__limit_submission_date__date = timezone.now())
	entries = []

	for goal in specifications:
		users = User.objects.filter(subject_student = goal.goal.topic.subject)

		for user in users:
			if not MyGoals.objects.filter(user = user, item = goal).exists():
				entries.append(MyGoals(user = user, item = goal, value = goal.ref_value))

	MyGoals.objects.bulk_create(entries)

def brodcast_dificulties(request, message, subject):
	msg = TalkMessages()
	msg.text = message
	msg.user = request.user
	msg.subject = subject

	simple_notify = textwrap.shorten(strip_tags(msg.text), width = 30, placeholder = "...")
	
	for p in subject.professor.all():
		talks = Conversation.objects.filter((Q(user_one = request.user) & Q(user_two__email = p.email)) | (Q(user_two = request.user) & Q(user_one__email = p.email)))
		
		if talks.count() > 0:
			msg.talk = talks[0]
		else:
			msg.talk = Conversation.objects.create(user_one = request.user, user_two = p)

		msg.save()

		notification = {
			"type": "chat",
			"subtype": subject.slug,
			"space": "subject",
			"user_icon": request.user.image_url,
			"notify_title": str(request.user),
			"simple_notify": simple_notify,
			"view_url": reverse("chat:view_message", args = (msg.id, ), kwargs = {}),
			"complete": render_to_string("chat/_message.html", {"talk_msg": msg}, request),
			"container": "chat-" + str(request.user.id),
			"last_date": _("Last message in %s")%(formats.date_format(msg.create_date, "SHORT_DATETIME_FORMAT"))
		}

		notification = json.dumps(notification)

		Group("user-%s" % p.id).send({'text': notification})

		sendChatPushNotification(p, msg)

		ChatVisualizations.objects.create(viewed = False, message = msg, user = p)

