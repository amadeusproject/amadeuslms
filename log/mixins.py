import json

from .models import Log

from users.models import User

class LogMixin(object):
	log_component = None
	log_context = None
	log_action = None
	log_resource = None

	def createLog(self, actor = None, component = '', log_action = '', log_resource = '', context = {}):
		if actor.is_authenticated:
			log = Log()
			log.user = str(actor)
			log.user_id = actor.id
			log.user_email = actor.email
			if self.log_context is not None:
				log.context = self.log_context
			else:
				log.context = context
			if self.log_component is not None:
				log.component = self.log_component
			else:
				log.component = component

			if self.log_action is not None:
				log.action = self.log_action
			else:
				log.action = log_action
			if self.log_resource is not None:
				log.resource = self.log_resource
			else:
				log.resource = log_resource

			log.save()

	def dispatch(self, request, *args, **kwargs):
		return super(LogMixin, self).dispatch(request, *args, **kwargs)