""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""


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