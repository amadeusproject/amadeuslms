from django.conf import settings
from functools import wraps
from .models import Action, Resource, Action_Resource, Log, Notification

def log_decorator(log_action = '', log_resource = ''):

	def _log_decorator(view_function):

		def _decorator(request, *args, **kwargs):

			response = view_function(request, *args, **kwargs)

			if request.user.is_authenticated and request.POST:
				action = Action.objects.filter(name = log_action)
				resource = Resource.objects.filter(name = log_resource)

				if not action:
					action = Action(name = log_action)
					action.save()
				else:
					action = action[0]

				if not resource:
					resource = Resource(name = log_resource)
					resource.save()
				else:
					resource = resource[0]

				action_resource = Action_Resource.objects.filter(action = action, resource = resource)

				if not action_resource:
					action_resource = Action_Resource(action = action, resource = resource)
					action_resource.save()
				else:
					action_resource = action_resource[0]

				log = Log()
				log.user = request.user
				log.action_resource = action_resource

				log.save()

			return response

		return wraps(view_function)(_decorator)

	return _log_decorator


def notification_decorator(read = False, message = '', actor = None, users = [], not_action='', not_resource='', resource_link=''):

	def _notification_decorator(view_function):

		def _decorator(request, *args, **kwargs):
			#Do something before the call

			response = view_function(request, *args, **kwargs)
			action = Action.objects.filter(name = not_action)
			resource = Resource.objects.filter(name = not_resource)
			if action.exists():
				action = action[0]
			else:
				action = Action(name = not_action)		
				action.save()

			if resource.exists():
				resource = resource[0]
			else:
				resource = Resource(name = not_resource, url= resource_link)
				resource.save()

			action_resource = Action_Resource.objects.filter(action = action, resource = resource)

			if action_resource.exists():
				action_resource = action_resource[0]
			else:
				action_resource = Action_Resource(action = action, resource = resource)
				action_resource.save()

			for user in users:
				notification = Notification(user=user, actor= actor, message=message, action_resource= action_resource)
				notification.save()


			#Do something after the call
			return response

		return wraps(view_function)(_decorator)

	return _notification_decorator
