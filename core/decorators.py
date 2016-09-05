import os
import datetime
from django.conf import settings
from functools import wraps

def log_decorator(log_action = ''):

	def _log_decorator(view_function):

		def _decorator(request, *args, **kwargs):

			response = view_function(request, *args, **kwargs)

			if request.user.is_authenticated and request.POST:
				date = datetime.datetime.now()

				message = date.strftime("%d/%m/%Y %H:%M:%S") + ' - ' + request.user.username + ' - ' + log_action + '\n'

				file_name = 'log_file_' + date.strftime("%d-%m-%Y") + '.txt'

				log_path = os.path.join(settings.LOGS_URL, file_name)

				log_file = open(log_path,'a+')
				log_file.write(message)
				log_file.close()

			return response

		return wraps(view_function)(_decorator)

	return _log_decorator