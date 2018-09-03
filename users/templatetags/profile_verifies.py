""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from django import template
from django.utils.translation import ugettext_lazy as _

from categories.models import Category
from subjects.models import Subject

register = template.Library()

@register.filter(name = 'is_coordinator')
def is_coordinator(user):
	cats = Category.objects.filter(coordinators = user)

	if len(cats) > 0:
		return ", ".join(cats.values_list('name', flat = True))

	return _('Is not a coordinator')

@register.filter(name = 'is_professor')
def is_professor(user):
	subs = Subject.objects.filter(professor = user)

	if len(subs) > 0:
		return ", ".join(subs.values_list('name', flat = True))

	return _('Is not a professor')

@register.filter(name = 'is_student')
def is_student(user):
	subs = Subject.objects.filter(students = user)

	if len(subs) > 0:
		return ", ".join(subs.values_list('name', flat = True))

	return _('Is not a student')
