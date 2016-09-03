import os
import datetime
from django.conf import settings

class LogMixin(object):
	log_action = ""

	def dispatch(self, request, *args, **kwargs):
		date = datetime.datetime.now()

		message = date.strftime("%d/%m/%Y %H:%M:%S") + ' - ' + request.user.username + ' - ' + self.log_action + '\n'

		file_name = 'log_file_' + date.strftime("%d-%m-%Y") + '.txt'

		log_path = os.path.join(settings.LOGS_URL, file_name)

		log_file = open(log_path,'a+')
		log_file.write(message)
		log_file.close()

		return super(LogMixin, self).dispatch(request, *args, **kwargs)