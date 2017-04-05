"""
	Middleware to register a log event for a session expire
	Called before session_security package clears the session and log out the user
"""

from datetime import datetime, timedelta
from session_security.settings import EXPIRE_AFTER
from session_security.utils import get_last_activity, set_last_activity

from log.models import Log

from .models import User
from django.utils.translation import ugettext as _u
from channels import Group
import json

class SessionExpireMiddleware(object):

	def process_request(self, request):
		if not request.user.is_authenticated():
			return

		now = datetime.now()

		if '_session_security' not in request.session:
			return
		
		delta = now - get_last_activity(request.session)
		expire_seconds = EXPIRE_AFTER

		if delta >= timedelta(seconds = expire_seconds):
			log = Log()
			log.user = str(request.user)
			log.user_id = request.user.id
			log.user_email = request.user.email
			log.context = {'condition': 'session_expire'}
			log.component = "user"
			log.action = "logout"
			log.resource = "system"

			log.save()

			users = User.objects.all().exclude(email = request.user.email)

			notification = {
				"type": "user_status",
				"user_id": str(request.user.id),
				"status": _u("Offline"),
				"status_class": "",
				"remove_class": "away"
			}

			notification = json.dumps(notification)

			for u in users:
				Group("user-%s" % u.id).send({'text': notification})