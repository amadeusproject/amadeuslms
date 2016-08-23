from django.utils.translation import ugettext_lazy as _
from django.db import models
from users.models import User

class Category(models.Model):

	name = models.CharField(_('Name'), max_length = 100, unique = True)
	slug = models.SlugField(_('Slug'), max_length = 100)
	create_date = models.DateField(_('Creation Date'), auto_now_add = True)

	class Meta:
		verbose_name = _('Category')
		verbose_name_plural = _('Categories')

	def __str__(self):
		return self.name

class Course(models.Model):

	name = models.CharField(_('Name'), max_length = 100, unique = True)
	slug = models.SlugField(_('Slug'), max_length = 100)
	objectivies = models.TextField(_('Objectivies'), blank = True)
	content = models.TextField(_('Content'), blank = True)
	max_students = models.PositiveIntegerField(_('Maximum Students'), blank = True)
	create_date = models.DateField(_('Creation Date'), auto_now_add = True)
	init_register_date = models.DateField(_('Register Date (Begin)'))
	end_register_date = models.DateField(_('Register Date (End)'))
	init_date = models.DateField(_('Begin of Course Date'))
	end_date = models.DateField(_('End of Course Date'))
	image = models.ImageField(verbose_name = _('Image'), blank = True, upload_to = 'courses/', default = 'no_image.jpg')
	category = models.ForeignKey(Category, verbose_name = _('Category'), default = 1)
	user = models.ForeignKey(User, verbose_name = _('User'), null = True)

	class Meta:

		verbose_name = _('Course')
		verbose_name_plural = _('Courses')

	def __str__(self):
		return self.name

class Module(models.Model):

	name = models.CharField(_('Name'), max_length = 100)
	slug = models.SlugField(_('Slug'), max_length = 100)
	description = models.TextField(_('Description'), blank = True)
	visible = models.BooleanField(_('Visible'), default = True, blank = True)
	create_date = models.DateField(_('Creation Date'), auto_now_add = True)
	course = models.ForeignKey(Course, verbose_name = _('Course'))

	class Meta:

		verbose_name = _('Module')
		verbose_name_plural = _('Modules')

	def __str__(self):
		return self.name