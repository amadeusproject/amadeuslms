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

from subjects.models import Subject, Tag
from students_group.models import StudentsGroup
from users.models import User

from .decorators import always_as_child

class Topic(models.Model):
	name = models.CharField(_('Name'), max_length = 200)
	slug = AutoSlugField(_("Slug"), populate_from = 'name', unique = True)
	description = models.TextField(_('Description'), blank = True)
	repository = models.BooleanField(_('Repository'), default = False)
	visible = models.BooleanField(_('Visible'), default = True)
	subject = models.ForeignKey(Subject, verbose_name = _('Subject'), related_name = 'topic_subject', null = True)
	order = models.PositiveSmallIntegerField(_('Order'), null = True)
	create_date = models.DateTimeField(_('Create Date'), auto_now_add = True)
	last_update = models.DateTimeField(_('Last Update'), auto_now = True)

	class Meta:
		verbose_name = _('Topic')
		verbose_name_plural = _('Topics')
		ordering = ['order']

	def __str__(self):
		return self.name

"""
	Abstract model to make easier to know which kind of Resource we are dealing with
"""
class KnowsChild(models.Model):
    # Make a place to store the class name of the child
    _my_subclass = models.CharField(max_length=200) 
 
    class Meta:
        abstract = True
 
    def as_child(self):
        return getattr(self, self._my_subclass)
 
    def save(self, *args, **kwargs):
        # save what kind we are.
        if not self._my_subclass:
        	self._my_subclass = self.__class__.__name__.lower() 
        	
        super(KnowsChild, self).save(*args, **kwargs)

class Resource(KnowsChild):
	name = models.CharField(_('Name'), max_length = 200)
	slug = AutoSlugField(_("Slug"), populate_from = 'name', unique = True)
	brief_description = models.TextField(_('Brief Description'), blank = True)
	show_window = models.BooleanField(_('Show in new window'), default = False)
	all_students = models.BooleanField(_('All Students'), default = False)
	visible = models.BooleanField(_('Visible'), default = True)
	order = models.PositiveSmallIntegerField(_('Order'), null = True)
	topic = models.ForeignKey(Topic, verbose_name = _('Topic'), related_name = "resource_topic", null = True)
	students = models.ManyToManyField(User, verbose_name = _('Students'), related_name = 'resource_students', blank = True)
	groups = models.ManyToManyField(StudentsGroup, verbose_name = _('Groups'), related_name = 'resource_groups', blank = True)
	tags = models.ManyToManyField(Tag, verbose_name = _('Markers'), related_name = 'resource_tags', blank = True)
	create_date = models.DateTimeField(_('Create Date'), auto_now_add = True)
	last_update = models.DateTimeField(_('Last Update'), auto_now = True)

	class Meta:
		verbose_name = _('Resource')
		verbose_name_plural = _('Resources')
		ordering = ['order']

	def __str__(self):
		return self.name

	"""
		Method to get the appropriated view link
		Must override in the child models
	"""
	@always_as_child
	def access_link(self):
		pass

	"""
		Method to get the appropriated update link
		Must override in the child models
	"""
	@always_as_child
	def update_link(self):
		pass

	"""
		Method to get the appropriated delete link
		Must override in the child models
	"""
	@always_as_child
	def delete_link(self):
		pass

	@always_as_child
	def delete_message(self):
		pass