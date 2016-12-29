import json

from .models import Log

from users.models import User

class LogMixin(object):
	log_component = ""
	log_context = {}
	log_action = ""
	log_resource = ""

	def createLog(self, actor = None, component = '', log_action = '', log_resource = '', context = {}):
		log = Log()
		log.user = actor
		log.context = context
		log.component = component
		log.action = log_action
		log.resource = log_resource

		log.save()

	def dispatch(self, request, *args, **kwargs):
		return super(LogMixin, self).dispatch(request, *args, **kwargs)