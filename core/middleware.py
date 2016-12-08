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

					oppened_logs = Log.objects.filter(user = request.user, context__contains={'timestamp_end': '-1'})

					for op_log in oppened_logs:
						if type(op_log.context) == dict:
							log_context = op_log.context
						else:
							log_context = json.loads(op_log.context)

						log_context['timestamp_end'] = str(int(time.time()))

						op_log.context = log_context

						op_log.save()
