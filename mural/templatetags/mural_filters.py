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
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.contrib.sessions.models import Session

from log.models import Log

from mural.models import MuralFavorites, MuralVisualizations

register = template.Library()

@register.filter(name = 'is_edited')
def is_edited(post):
	if post.edited:
		return _("(Edited)")

	return ""

@register.filter(name = 'action_icon')
def action_icon(action):
	icon = ""

	if action == "comment":
		icon = "fa-commenting-o"
	elif action == "help":
		icon = "fa-comments-o"

	return icon

@register.filter(name = 'fav_label')
def fav_label(post, user):
	if MuralFavorites.objects.filter(post = post, user = user).exists():
		return _('Unfavorite')

	return _('Favorite')

@register.filter(name = 'fav_action')
def fav_action(post, user):
	if MuralFavorites.objects.filter(post = post, user = user).exists():
		return "unfavorite"

	return "favorite"

@register.filter(name = 'fav_class')
def fav_class(post, user):
	if MuralFavorites.objects.filter(post = post, user = user).exists():
		return "btn_unfav"

	return "btn_fav"

@register.filter(name = 'unviewed')
def unviewed(category, user):
	count = MuralVisualizations.objects.filter(Q(user = user) & Q(viewed = False) & (Q(post__categorypost__space = category) | Q(comment__post__categorypost__space = category))).count()

	return count

@register.filter(name = 'sub_unviewed')
def sub_unviewed(subject, user):
	count = MuralVisualizations.objects.filter(Q(user = user) & Q(viewed = False) & (Q(post__subjectpost__space = subject) | Q(comment__post__subjectpost__space = subject))).count()

	return count

@register.filter(name = 'show_settings')
def show_settings(post, user):
	if user.is_staff:
		return True

	if post.user == user:
		return True

	if post._my_subclass == "categorypost":
		if user in post.categorypost.space.coordinators.all():
			return True

	if post._my_subclass == "subjectpost":
		if user in post.subjectpost.space.professor.all():
			return True

		if user in post.subjectpost.space.category.coordinators.all():
			return True

	return False

@register.filter(name = 'show_settings_comment')
def show_settings_comment(comment, user):
	if user.is_staff:
		return True

	if comment.user == user:
		return True

	if comment.post._my_subclass == "categorypost":
		if user in comment.post.categorypost.space.coordinators.all():
			return True

	if comment.post._my_subclass == "subjectpost":
		if user in comment.post.subjectpost.space.professor.all():
			return True

		if user in comment.post.subjectpost.space.category.coordinators.all():
			return True

	return False

@register.filter(name = 'has_resource')
def has_resource(post):
	if post._my_subclass == 'subjectpost':
		if post.subjectpost.resource:
			return _("about") + " <span class='post_resource'>" + str(post.subjectpost.resource) + "</span>"

	return ""

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

@register.filter(name = 'chat_space')
def chat_space(post):
	if post._my_subclass == "subjectpost":
		return post.subjectpost.space.id

	return 0

@register.filter(name = 'chat_space_type')
def chat_space_type(post):
	if post._my_subclass == "subjectpost":
		return "subject"

	return "general"