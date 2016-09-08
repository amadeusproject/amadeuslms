from django.conf import settings
from functools import wraps
from .models import Action, Resource, Action_Resource, Log

def log_decorator(log_action = '', log_resource = ''):

	def _log_decorator(view_function):

		def _decorator(request, *args, **kwargs):

			response = view_function(request, *args, **kwargs)

			if request.user.is_authenticated and request.POST:
				action = Action.objects.filter(name = log_action)
				resource = Resource.objects.filter(name = log_resource)

				action_resource = Action_Resource.objects.filter(action = action, resource = resource)[0]

				log = Log()
				log.user = request.user
				log.action_resource = action_resource

				log.save()

			return response

		return wraps(view_function)(_decorator)

	return _log_decorator
