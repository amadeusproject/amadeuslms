""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""


import time
import json
from django.core.urlresolvers import resolve
from django.shortcuts import get_object_or_404

from .models import Log

class TimeSpentMiddleware(object):
	def __init__(self, get_response = None):
		self.get_response = get_response

	def process_request(self, request):
		app_names = resolve(request.path).app_names

		if not 'admin' in app_names:
			if not request.is_ajax():
				if not request.path.startswith('/uploads/'):
					log_id = request.session.get('log_id', None)

					if not log_id is None:
						log = get_object_or_404(Log, id = log_id)

						if type(log.context) == dict:
							log_context = log.context
						else:
							log_context = json.loads(log.context)

						log_context['timestamp_end'] = str(int(time.time()))

						log.context = log_context

						log.save()

						request.session['log_id'] = None

					if request.user.is_authenticated:
						oppened_logs = Log.objects.filter(user = request.user, context__contains={'timestamp_end': '-1'})

						for op_log in oppened_logs:
							if type(op_log.context) == dict:
								log_context = op_log.context
							else:
								log_context = json.loads(op_log.context)

							log_context['timestamp_end'] = str(int(time.time()))

							op_log.context = log_context

							op_log.save()