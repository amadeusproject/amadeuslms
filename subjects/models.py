""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from django.db import models
from django.contrib.postgres.fields import JSONField
from django.db.models import Q

from autoslug.fields import AutoSlugField

from django.utils.translation import ugettext_lazy as _

from users.models import User

from django.core.exceptions import ValidationError

from categories.models import Category
import datetime

class Tag(models.Model):
    name = models.CharField( _("Name"), unique = True,max_length= 200, blank = True)
    
    def __str__(self):
        return self.name

class Subject(models.Model):

    name = models.CharField( _("Name"), unique = False, max_length= 200)
    slug = AutoSlugField(_("Slug"),populate_from='name',unique=True)

    description_brief = models.TextField(_("simpler description"), blank=True)
    description = models.TextField(_("description"), blank= True)
    visible = models.BooleanField(_("visible"))

    init_date = models.DateField(_('Begin of Subject Date'))
    end_date = models.DateField(_('End of Subject Date'))

    tags = models.ManyToManyField(Tag, verbose_name='tags', blank=True)

    create_date = models.DateTimeField(_('Creation Date'), auto_now_add = True)
    update_date = models.DateTimeField(_('Date of last update'), auto_now=True)

    subscribe_begin = models.DateField(_('Begin Subscribe'))
    subscribe_end = models.DateField(_('End Subscribe'))

    professor = models.ManyToManyField(User, related_name="professors", blank=True)
    students = models.ManyToManyField(User,verbose_name=_('Students'), related_name='subject_student', blank = True)

    category = models.ForeignKey(Category, related_name="subject_category", null=True)

    max_upload_size = models.IntegerField(_("Maximum upload size"), default=1024, null=True)

    display_avatar = models.BooleanField(_("Display avatar to students?"), default=False)
    
    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"
        ordering = ['name']

    def __str__(self):
        return self.name
    
    def get_participants(self):
        data = User.objects.filter(
            Q(is_staff = True) | Q(subject_student__slug = self.slug) |
            Q(professors__slug = self.slug) |
            Q(coordinators__subject_category__slug = self.slug)
            ).distinct()

        return data

"""
class Log_Consultas(models.Model):
	component = models.TextField(_('Component (Module / App)'), blank=True,
    null=True)
	context = JSONField(_('Context'), blank=True,
    null=True)
	action = models.TextField(_('Action'), blank=True,
    null=True)
	resource = models.TextField(_('Resource'), blank=True,
    null=True)
	user = models.CharField(_('Actor'), max_length = 100)
	user_id = models.IntegerField(_('Actor id'))
	user_email = models.EmailField(_('Actor Mail'), blank=True,
    null=True)
	datetime = models.DateTimeField(_("Date and Time of action"), blank=True,
    null=True)
	is_admin = models.BooleanField(_("Admin"), default=False)
	is_teacher = models.BooleanField(_("Teacher"), default=False)
	teacher_subjects = models.ManyToManyField(Subject, verbose_name="List of subjects", related_name='List_of_subjects')
	is_student = models.BooleanField(_("Student"), default=False)
	student_subjects = models.ManyToManyField(Subject, verbose_name="List of subjects you are a student in", related_name='List_of_subjects_you_are_a_student_in')
	is_coordinator = models.BooleanField(_("Coordinator"), default=False)
	subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name="Subject", blank=True,
    null=True)
    

	class Meta:
		verbose_name = _('Log for query')
		verbose_name_plural = _('Logs for queries')

	def __str__(self):
		return str(self.user) + ' / ' + self.component
	
	# def indexing(self):
	# 	if self.context == '':
	# 		self.context = {}
		
	# 	obj = LogIndex(meta={'id': self.id}, id=self.id, component=self.component, action=self.action, resource=self.resource, user=self.user, user_id=self.user_id, datetime=self.datetime, context=self.context)

	# 	obj.save()

	# 	return obj.to_dict(include_meta=True)
"""