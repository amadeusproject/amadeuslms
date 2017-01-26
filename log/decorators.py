import json
import time
from functools import wraps
from django.shortcuts import get_object_or_404

from .models import Log

def log_decorator(log_component = '', log_action = '', log_resource = ''):

	def _log_decorator(view_function):

		def _decorator(request, *args, **kwargs):
			user = None

			if request.user.is_authenticated:
				user = request.user				

			response = view_function(request, *args, **kwargs)

			log_context = {}

			if hasattr(request, 'log_context'):
				log_context = request.log_context

			if user:				
				log = Log()
				log.user = str(user)
				log.user_id = user.id
				log.user_email = user.email
				log.component = log_component
				log.context = log_context
				log.action = log_action
				log.resource = log_resource

				log.save()

			return response

		return wraps(view_function)(_decorator)

	return _log_decorator

def log_decorator_ajax(log_component = '', log_action = '', log_resource = ''):

	def _log_decorator_ajax(view_function):

		def _decorator(request, *args, **kwargs):
			view_action = request.GET.get("action")

			if view_action == 'open':
				if request.user.is_authenticated:
					
					log = Log()
					log.user = str(request.user)
					log.user_id = request.user.id
					log.user_email = request.user.email
					log.component = log_component
					log.context = ""
					log.action = log_action
					log.resource = log_resource

					log.save()

					response = view_function(request, *args, **kwargs)
					
					log_context = {}

					if hasattr(request, 'log_context'):
						log_context = request.log_context

					log = Log.objects.latest('id')
					log.context = log_context
					log.save()
					
			elif view_action == 'close':
				if request.user.is_authenticated:
					log = get_object_or_404(Log, id = request.GET.get('log_id'))

					if type(log.context) == dict:
						log_context = log.context
					else:
						log_context = json.loads(log.context)

					log_context['timestamp_end'] = str(int(time.time()))

					log.context = log_context

					log.save()

					response = view_function(request, *args, **kwargs)

			return response

		return wraps(view_function)(_decorator)

	return _log_decorator_ajax