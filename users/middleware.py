""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

"""
	Middleware to register a log event for a session expire
	Called before session_security package clears the session and log out the user
"""

from datetime import datetime, timedelta
from session_security.settings import EXPIRE_AFTER
from session_security.utils import get_last_activity, set_last_activity

from log.models import Log

from .models import User
from django.utils.translation import ugettext as _u
from channels import Group
import json

class SessionExpireMiddleware(object):

	def process_request(self, request):
		if not request.user.is_authenticated():
			return

		now = datetime.now()

		if '_session_security' not in request.session:
			return
		
		delta = now - get_last_activity(request.session)
		expire_seconds = EXPIRE_AFTER

		if delta >= timedelta(seconds = expire_seconds):
			log = Log()
			log.user = str(request.user)
			log.user_id = request.user.id
			log.user_email = request.user.email
			log.context = {'condition': 'session_expire'}
			log.component = "user"
			log.action = "logout"
			log.resource = "system"

			log.save()

			users = User.objects.all().exclude(email = request.user.email)

			notification = {
				"type": "user_status",
				"user_id": str(request.user.id),
				"status": _u("Offline"),
				"status_class": "",
				"remove_class": "away"
			}

			notification = json.dumps(notification)

			for u in users:
				Group("user-%s" % u.id).send({'text': notification})