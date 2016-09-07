from django.conf import settings
from .models import Action, Resource, Action_Resource, Log

class LogMixin(object):
	log_action = ""
	log_resource = ""

	def dispatch(self, request, *args, **kwargs):
		action = Action.objects.filter(name = self.log_action)
		resource = Resource.objects.filter(name = self.log_resource)

		action_resource = Action_Resource.objects.filter(action = action, resource = resource)[0]

		log = Log()
		log.user = request.user
		log.action_resource = action_resource

		log.save()

		return super(LogMixin, self).dispatch(request, *args, **kwargs)