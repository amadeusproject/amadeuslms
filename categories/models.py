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
from users.models import User

class Category(models.Model):
	"""Represents a Course """

	name = models.CharField(_("Name"), max_length = 100, blank = False, null = False, unique = True)
	slug = AutoSlugField(_("Slug"), populate_from = 'name', unique = True)
	description = models.CharField(_("description"), max_length = 300,blank = True, null = True)
	visible = models.BooleanField(_("visible"), default = True)
	coordinators = models.ManyToManyField(User, related_name = "coordinators", blank = True)
	create_date = models.DateTimeField(_('Creation Date'), auto_now_add = True)
	modified_date = models.DateTimeField(_('Modified Date'), auto_now_add = True)

	REQUIRED_FIELDS = ['name',]
	class Meta:
		verbose_name = _('Category')
		verbose_name_plural = _('Categories')

	def __str__(self):
		return self.name
