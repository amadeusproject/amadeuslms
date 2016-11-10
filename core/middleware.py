from datetime import datetime
import time
from django.core.urlresolvers import resolve
from django.shortcuts import get_object_or_404
import json

from core.models import Log

class TimeSpentMiddleware(object):
	def __init__(self, get_response = None):
		self.get_response = get_response

	def process_request(self, request):
		app_names = resolve(request.path).app_names

		if not 'admin' in app_names:
			if not request.is_ajax():
				log_id = request.session.get('log_id', None)

				if not log_id is None:
					log = get_object_or_404(Log, id = log_id)

					if type(log.context) == dict:
						log_context = log.context
					else:
						log_context = json.loads(log.context)

					log_context['timestamp_end'] = str(int(time.time()))

					log.context = log_context

					log.save()

					request.session['log_id'] = None
