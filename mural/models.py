from django.db import models
from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from categories.models import Category
from subjects.models import Subject
from topics.models import KnowsChild, Resource
from users.models import User

def validate_img_extension(value):
	valid_formats = ['image/jpeg','image/x-citrix-jpeg','image/png','image/x-citrix-png','image/x-png']
	
	if hasattr(value.file, 'content_type'):
		if not value.file.content_type in valid_formats:
			raise ValidationError(_('File not supported.'))

class Mural(KnowsChild):
	action = models.CharField(_('Action'), max_length = 100, choices = (("comment", _("Comment")), ("help", _("Ask for Help"))), blank = True)
	post = models.TextField(_('Post'), blank = True)
	image = models.ImageField(verbose_name = _('Image'), null=True, blank = True, upload_to = 'posts/', validators = [validate_img_extension])
	user = models.ForeignKey(User, verbose_name = _('User'), related_name = "post_user", null = True)
	create_date = models.DateTimeField(_('Create Date'), auto_now_add = True)
	last_update = models.DateTimeField(_('Last Update'), auto_now = True)

class GeneralPost(Mural):
	space = models.IntegerField(_('Space'), default = 0, blank = True)

class CategoryPost(Mural):
	space = models.ForeignKey(Category, verbose_name = ('Category'), related_name = 'post_category')

class SubjectPost(Mural):
	space = models.ForeignKey(Subject, verbose_name = _('Subject'), related_name = 'post_subject')
	resource = models.ForeignKey(Resource, verbose_name = _('Resource'), related_name = 'post_resource', null = True)

class Comment(models.Model):
	comment = models.TextField(_('Comment'), blank = True)
	image = models.ImageField(verbose_name = _('Image'), null=True, blank = True, upload_to = 'posts/comments/', validators = [validate_img_extension])
	post = models.ForeignKey(Mural, verbose_name = _('Post'), related_name = 'comment_post')
	user = models.ForeignKey(User, verbose_name = _('User'), related_name = "comment_user", null = True)
	create_date = models.DateTimeField(_('Create Date'), auto_now_add = True)
	last_update = models.DateTimeField(_('Last Update'), auto_now = True)