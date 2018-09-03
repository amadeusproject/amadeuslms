""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

import datetime
from django import template
from django.db.models import Q

from chat.models import ChatVisualizations
from mural.models import MuralVisualizations
from notifications.models import Notification

register = template.Library()

@register.filter(name = 'subject_count')
def subject_count(category, user):
	total = 0
	
	if not user.is_staff:
		for subject in category.subject_category.all():
			if user in subject.students.all() or user in subject.professor.all() or user in subject.category.coordinators.all():
				total += 1
	else:		
		total = category.subject_category.count()

	return total

@register.inclusion_tag('subjects/badge.html')
def notifies_number(subject, user):
	context = {}

	context['number'] = Notification.objects.filter(task__resource__topic__subject = subject, creation_date = datetime.datetime.now(), viewed = False, user = user).count()
	context['custom_class'] = 'pendencies_notify'
	
	return context

@register.inclusion_tag('subjects/badge.html')
def mural_number(subject, user):
	context = {}

	context['number'] = MuralVisualizations.objects.filter(Q(user = user) & Q(viewed = False) & (Q(post__subjectpost__space = subject) | Q(comment__post__subjectpost__space = subject))).count()
	context['custom_class'] = 'mural_notify'
	
	return context

@register.inclusion_tag('subjects/badge.html')
def chat_number(subject, user):
	context = {}

	context['number'] = ChatVisualizations.objects.filter(Q(user = user) & Q(viewed = False) & Q(message__subject = subject) & (Q(user__is_staff = True) | Q(message__subject__students = user) | Q(message__subject__professor = user) | Q(message__subject__category__coordinators = user))).distinct().count()
	context['custom_class'] = 'chat_notify'
	
	return context

@register.inclusion_tag('subjects/badge.html')
def resource_mural_number(resource, user):
	context = {}

	context['number'] = MuralVisualizations.objects.filter(Q(user = user) & Q(viewed = False) & (Q(post__subjectpost__resource = resource) | Q(comment__post__subjectpost__resource = resource))).count()
	context['custom_class'] = 'mural_resource_notify'
	
	return context

@register.filter(name = 'aftertoday')
def after_today(date):
	if date > datetime.datetime.today().date():
		return True
	return False