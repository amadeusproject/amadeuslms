""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from django.db import models
from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _, pgettext_lazy

from topics.decorators import always_as_child

from categories.models import Category
from subjects.models import Subject
from topics.models import KnowsChild, Resource
from users.models import User

valid_formats = ['image/jpeg','image/x-citrix-jpeg','image/png','image/x-citrix-png','image/x-png','image/gif']

def validate_img_extension(value):
	if hasattr(value.file, 'content_type'):
		if not value.file.content_type in valid_formats:
			raise ValidationError(_('File not supported.'))

class Mural(KnowsChild):
	action = models.CharField(_('Action'), max_length = 100, default = "comment", choices = (("comment", pgettext_lazy("modal","Comment")), ("help", pgettext_lazy("modal","Ask for Help"))))
	post = models.TextField(_('Post'), blank = True)
	image = models.ImageField(verbose_name = _('Image'), null=True, blank = True, upload_to = 'posts/', validators = [validate_img_extension])
	user = models.ForeignKey(User, verbose_name = _('User'), related_name = "post_user", null = True)
	create_date = models.DateTimeField(_('Create Date'), auto_now_add = True)
	last_update = models.DateTimeField(_('Last Update'), auto_now = True)
	edited = models.BooleanField(_('Edited'), default = False)

	@always_as_child
	def get_id(self):
		pass

	@always_as_child
	def get_space(self):
		pass

	@always_as_child
	def get_space_slug(self):
		pass

	@always_as_child
	def update_link(self):
		pass

	@always_as_child
	def delete_link(self):
		pass

class GeneralPost(Mural):
	space = models.IntegerField(_('Space'), default = 0, blank = True)

	def get_id(self):
		return self.id

	def get_space(self):
		return self.space

	def get_space_slug(self):
		return ""

	def update_link(self):
		return "mural:update_general"

	def delete_link(self):
		return "mural:delete_general"

class CategoryPost(Mural):
	space = models.ForeignKey(Category, verbose_name = ('Category'), related_name = 'post_category', null = True)

	def get_id(self):
		return self.id

	def get_space(self):
		return self.space.id

	def get_space_slug(self):
		return self.space.slug

	def update_link(self):
		return "mural:update_category"

	def delete_link(self):
		return "mural:delete_category"

class SubjectPost(Mural):
	space = models.ForeignKey(Subject, verbose_name = _('Subject'), related_name = 'post_subject')
	resource = models.ForeignKey(Resource, verbose_name = _('Resource'), related_name = 'post_resource', null = True, blank = True)

	def get_id(self):
		return self.id

	def get_space(self):
		return self.space.id

	def get_space_slug(self):
		return self.space.slug

	def update_link(self):
		return "mural:update_subject"

	def delete_link(self):
		return "mural:delete_subject"

class Comment(models.Model):
	comment = models.TextField(_('Comment'), blank = True)
	image = models.ImageField(verbose_name = _('Image'), null=True, blank = True, upload_to = 'posts/comments/', validators = [validate_img_extension])
	post = models.ForeignKey(Mural, verbose_name = _('Post'), related_name = 'comment_post', null = True)
	user = models.ForeignKey(User, verbose_name = _('User'), related_name = "comment_user", null = True)
	create_date = models.DateTimeField(_('Create Date'), auto_now_add = True)
	last_update = models.DateTimeField(_('Last Update'), auto_now = True)
	edited = models.BooleanField(_('Edited'), default = False)

"""
	Model to handle posts visualizations
"""
class MuralVisualizations(models.Model):
	viewed = models.BooleanField(_('Viewed'), default = False)
	post = models.ForeignKey(Mural, verbose_name = _('Post'), related_name = 'visualization_post', null = True)
	comment = models.ForeignKey(Comment, verbose_name = _('Comment'), related_name = 'visualization_comment', null = True)
	user = models.ForeignKey(User, verbose_name = _('User'), related_name = "visualization_user", null = True)
	date_viewed = models.DateTimeField(_('Date/Time Viewed'), null = True, blank = True)

"""
	Model to handle users favorite posts
"""
class MuralFavorites(models.Model):
	post = models.ForeignKey(Mural, verbose_name = _('Post'), related_name = 'favorites_post', null = True)
	user = models.ForeignKey(User, verbose_name = _('User'), related_name = "favorites_user", null = True)
