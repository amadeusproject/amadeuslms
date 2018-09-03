""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from django.db import models
from autoslug.fields import AutoSlugField
from django.utils.translation import ugettext_lazy as _

from subjects.models import Subject
from users.models import User

class StudentsGroup(models.Model):
	name = models.CharField(_('Name'), max_length = 200)
	slug = AutoSlugField(_("Slug"), populate_from = 'name', unique = True)
	description = models.TextField(_('Description'), blank = True)
	subject = models.ForeignKey(Subject, verbose_name = _('Subject'), related_name = 'group_subject', null = True)
	participants = models.ManyToManyField(User, verbose_name = _('Participants'), related_name = 'group_participants', blank = True)
	create_date = models.DateTimeField(_('Create Date'), auto_now_add = True)
	last_update = models.DateTimeField(_('Last Update'), auto_now = True)

	class Meta:
		verbose_name = _('Students Group')
		verbose_name_plural = _('Students Groups')
		ordering = ['name']

	def __str__(self):
		return self.name