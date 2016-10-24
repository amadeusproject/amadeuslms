from django.utils.translation import ugettext_lazy as _
from django.db import models
import datetime
from autoslug.fields import AutoSlugField
from users.models import User
from core.models import Resource, MimeType
from s3direct.fields import S3DirectField

from django.core.urlresolvers import reverse
from core.models import Resource

class CourseCategory(models.Model):

	name = models.CharField(_('Name'), max_length = 100, unique = True)
	slug = AutoSlugField(_("Slug"),populate_from='name',unique=True)
	create_date = models.DateField(_('Creation Date'), auto_now_add = True)

	class Meta:
		verbose_name = _('Category')
		verbose_name_plural = _('Categories')

	def __str__(self):
		return self.name

class CategorySubject(models.Model):
	name = models.CharField(_('Name'), max_length=100, unique=True)
	slug = AutoSlugField(_("Slug"), populate_from='name', unique=True)
	create_date = models.DateField(_('Creation Date'), auto_now_add=True)

	class Meta:
		verbose_name = _('Category')
		verbose_name_plural = _('Categories')

	def __str__(self):
		return self.name

class Course(models.Model):

	name = models.CharField(_('Name'), max_length = 100)
	slug = AutoSlugField(_("Slug"),populate_from='name',unique=True)
	objectivies = models.TextField(_('Objectivies'), blank = True)
	content = models.TextField(_('Content'), blank = True)
	max_students = models.PositiveIntegerField(_('Maximum Students'), blank = True)
	create_date = models.DateField(_('Creation Date'), auto_now_add = True)
	init_register_date = models.DateField(_('Register Date (Begin)'))
	end_register_date = models.DateField(_('Register Date (End)'))
	init_date = models.DateField(_('Begin of Course Date'))
	end_date = models.DateField(_('End of Course Date'))
	image = models.ImageField(verbose_name = _('Image'), blank = True, upload_to = 'courses/')
	category = models.ForeignKey(CourseCategory, verbose_name = _('Category'), related_name='course_category')
	professors = models.ManyToManyField(User,verbose_name=_('Professors'), related_name='courses_professors')
	students = models.ManyToManyField(User,verbose_name=_('Students'), related_name='courses_student', blank = True)
	public = models.BooleanField(_('Public'))

	class Meta:
		ordering = ('create_date','name')
		verbose_name = _('Course')
		verbose_name_plural = _('Courses')

	def __str__(self):
		return self.name

	def get_absolute_url (self):
		return reverse('course:view', kwargs={'slug': self.slug})

	def show_subscribe(self):
		today = datetime.date.today()
		return today >= self.init_register_date and today <= self.end_register_date

	def duration(self):
		return self.end_date - self.init_date

class Subject(models.Model):

	name = models.CharField(_('Name'), max_length = 100)
	slug = AutoSlugField(_("Slug"),populate_from='name',unique=True)
	description = models.TextField(_('Description'), blank = True)
	visible = models.BooleanField(_('Visible'), default = False)
	init_date = models.DateField(_('Begin of Subject Date'))
	end_date = models.DateField(_('End of Subject Date'))
	create_date = models.DateTimeField(_('Creation Date'), auto_now_add = True)
	update_date = models.DateTimeField(_('Date of last update'), auto_now=True)
	course = models.ForeignKey(Course, verbose_name = _('Course'), related_name="subjects")
	category = models.ForeignKey(CategorySubject, verbose_name = _('Category'), related_name='subject_category',null=True)
	professors = models.ManyToManyField(User,verbose_name=_('Professors'), related_name='professors_subjects')
	students = models.ManyToManyField(User,verbose_name=_('Students'), related_name='subject_student', blank = True)

	class Meta:
		ordering = ('create_date','name')
		verbose_name = _('Subject')
		verbose_name_plural = _('Subjects')

	def __str__(self):
		return self.name

	def show_subscribe(self):
		today = datetime.date.today()

		return today < self.init_date

class Topic(models.Model):

	name = models.CharField(_('Name'), max_length = 100)
	slug = AutoSlugField(_("Slug"),populate_from='name',unique=True)
	description = models.TextField(_('Description'), blank = True)
	create_date = models.DateTimeField(_('Creation Date'), auto_now_add = True)
	update_date = models.DateTimeField(_('Date of last update'), auto_now=True)
	subject = models.ForeignKey(Subject, verbose_name = _('Subject'))
	owner = models.ForeignKey(User, verbose_name = _('Owner'))
	visible = models.BooleanField(_('Visible'), default=False)

	class Meta:
		ordering = ('create_date','name')
		verbose_name = _('Topic')
		verbose_name_plural = _('Topics')

	def __str__(self):
		return self.name

"""
It is one kind of possible resources available inside a Topic.
Activity is something that has a deadline and has to be delivered by the student
"""
class Activity(Resource):
	topic = models.ForeignKey(Topic, verbose_name = _('Topic'), related_name='activities')
	limit_date = models.DateField(_('Deliver Date'))
	students = models.ManyToManyField(User, verbose_name = _('Students'), related_name='activities')
	all_students = models.BooleanField(_('All Students'), default=False)

class ActivityFile(models.Model):
	pdf = S3DirectField(dest='activitys')
	diet = models.ForeignKey('Activity', related_name='files')
	name = models.CharField(max_length=100)

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = u"Activity File"
		verbose_name_plural = u"Activitys Files"

"""
It represents any Material inside a topic, be it a file, a link, etc.
"""
class Material(Resource):
	topic = models.ForeignKey(Topic, verbose_name = _('Topic'), related_name='materials')
	students = models.ManyToManyField(User, verbose_name = _('Students'), related_name='materials')
	all_students = models.BooleanField(_('All Students'), default=False)
	
class FileMaterial(models.Model):
	material = models.ForeignKey(Material, verbose_name = _('Material'), related_name='material_file')
	file = models.FileField(upload_to='uploads/%Y/%m/%d')
	name = models.CharField(max_length=100)

class LinkMaterial(models.Model):
	material = models.ForeignKey(Material, verbose_name = _('Material'), related_name='material_link')
	name = models.CharField(max_length=100)
	description = models.TextField()
	url = models.URLField('Link', max_length=300)		

"""
It is a category for each subject.
"""
class SubjectCategory(models.Model):
	name = models.CharField(_('Name'), max_length= 100)
	slug = AutoSlugField(_("Slug"),populate_from='name',unique=True)
	description = models.TextField(_('Description'), blank = True)
	subjects = models.ManyToManyField(Subject)

	class Meta:
		verbose_name = _('subject category')
		verbose_name_plural = _('subject categories')
