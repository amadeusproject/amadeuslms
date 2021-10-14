""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""


import json
import time
from django.utils import timezone
from functools import wraps
from django.shortcuts import get_object_or_404

from .models import Log
from pendencies.models import Pendencies, PendencyDone

def log_decorator(log_component = '', log_action = '', log_resource = ''):

	def _log_decorator(view_function):

		def _decorator(request, *args, **kwargs):
			user = None

			#Get user before logout
			if request.user.is_authenticated:
				user = request.user				

			response = view_function(request, *args, **kwargs)

			#Get user after login
			if user is None and request.user.is_authenticated:
				user = request.user

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

				if log.component == 'resources' and not user.is_staff:
					resource = log.context[log.resource + '_id'] if log.resource + '_id' in log.context else 0

					if not resource == 0:
						pendency = Pendencies.objects.filter(action = log.action, resource__id = resource, resource__visible = True).order_by('-id')

						if pendency.exists():
							pendency = pendency.get()

							if ((not pendency.end_date or timezone.now() <= pendency.end_date) or (pendency.limit_date and timezone.now() <= pendency.limit_date) or (not pendency.end_date or (not pendency.limit_date and timezone.now() > pendency.end_date))):
								if actor in pendency.resource.students.all() or (pendency.resource.all_students and actor in pendency.resource.topic.subject.students.all()):
									if not PendencyDone.objects.filter(pendency = pendency, student = actor).exists():
										pendencyDone = PendencyDone()
										pendencyDone.pendency = pendency
										pendencyDone.student = actor
										pendencyDone.done_date = timezone.now()

										if not pendency.begin_date or not pendency.end_date:
											pendencyDone.late = False
										elif pendency.begin_date > timezone.now():
											pendencyDone.late = False
										elif pendency.begin_date <= timezone.now() <= pendency.end_date:
											pendencyDone.late = False
										elif (pendency.limit_date and pendency.end_date < timezone.now() <= pendency.limit_date) or (not pendency.limit_date and pendency.end_date < timezone.now()):
											pendencyDone.late = True

										pendencyDone.save()

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
					log.context = {}
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