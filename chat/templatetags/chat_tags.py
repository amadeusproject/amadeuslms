""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from django import template
from django.conf import settings
from django.utils import timezone
from django.db.models import Count, F, Q
from django.utils.translation import ugettext_lazy as _
from django.contrib.sessions.models import Session

from log.models import Log

from chat.models import TalkMessages, ChatVisualizations, ChatFavorites

register = template.Library()

@register.assignment_tag(name = 'is_online')
def is_online(user):
	expire_time = settings.SESSION_SECURITY_EXPIRE_AFTER
	now = timezone.now()
	
	activities = Log.objects.filter(user_id = user.id).order_by('-datetime')

	if activities.count() > 0:
		last_activity = activities[0]

		if last_activity.action != 'logout':
			if (now - last_activity.datetime).total_seconds() < expire_time:
				return "active"
			else:
				return "away"
	
	return ""

@register.filter(name = 'status_text')
def status_text(status):
	if status == "active":
		return _("Online")
	elif status == "away":
		return _('Away')
	else:
		return _("Offline")

@register.assignment_tag(name = 'chat_user')
def chat_user(user, chat):
	if chat.user_one == user:
		return chat.user_two

	return chat.user_one

@register.filter(name = 'last_message')
def last_message(chat):
	last_message = TalkMessages.objects.filter(talk = chat).order_by('-create_date')[0]

	return last_message.create_date

@register.filter(name = 'notifies')
def notifies(chat, user):
	total = ChatVisualizations.objects.filter(message__talk = chat, user = user, viewed = False).count()

	return total

@register.filter(name = 'fav_label')
def fav_label(message, user):
	if ChatFavorites.objects.filter(message = message, user = user).exists():
		return _('Unfavorite')

	return _('Favorite')

@register.filter(name = 'fav_action')
def fav_action(message, user):
	if ChatFavorites.objects.filter(message = message, user = user).exists():
		return "unfavorite"

	return "favorite"

@register.filter(name = 'fav_class')
def fav_class(message, user):
	if ChatFavorites.objects.filter(message = message, user = user).exists():
		return "btn_unfav"

	return "btn_fav"

@register.filter(name = 'notifies_subject')
def notifies_subject(subject, user):
	total = ChatVisualizations.objects.filter(Q(message__subject = subject, user = user, viewed = False)  & (Q(user__is_staff = True) | Q(message__subject__students = user) | Q(message__subject__professor = user) | Q(message__subject__category__coordinators = user))).distinct().count()

	return total