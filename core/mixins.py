from django.conf import settings
from .models import Action, Resource, Action_Resource, Log, Notification
from users.models import User

class LogMixin(object):
	log_action = ""
	log_resource = ""

	def dispatch(self, request, *args, **kwargs):
		action = Action.objects.filter(name = self.log_action)
		resource = Resource.objects.filter(name = self.log_resource)

		if not action:
			action = Action(name = self.log_action)
			action.save()
		else:
			action = action[0]

		if not resource:
			resource = Resource(name = self.log_resource)
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

		return super(LogMixin, self).dispatch(request, *args, **kwargs)

class NotificationMixin(object):
	message = ""
	read = False
	not_action = ''
	not_resource = ''

	def createNotification(self, message='', actor=None, users = User.objects.all(), not_action = '', not_resource='', resource_link=''): #the default will be a broadcast
		action = Action.objects.filter(name = self.not_action)
		resource = Resource.objects.filter(name = not_resource)
		print(resource_link)
		if action.exists():
			action = action[0]
		else:
			action = Action(name = self.not_action)
			action.save()

		if resource.exists():
			resource = resource[0]
		else:
			resource = Resource(name = self.not_resource, link= resource_link)
			print(resource)
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


	def dispatch(self, request, *args, **kwargs):
		"""
		Not quite sure how to do about it"""
		return super(NotificationMixin, self).dispatch(request, *args, **kwargs)