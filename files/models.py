from django.db import models
from django.utils.translation import ugettext_lazy as _
from core.models import MimeType
from courses.models import Material
from users.models import User

"""
	Function to return the path where the file should be saved
"""
def file_path(instance, filename):
	return '/'.join([instance.topic.subject.course.slug, instance.topic.subject.slug, instance.topic.slug, filename])


"""
	It's one kind of activity available for a Topic.
	It's like a support material for the students.
"""
class TopicFile(Material):

	professor = models.ManyToManyField(User,verbose_name=_('Professors'), related_name='file_professors')
	description = models.TextField(_('Description'), blank=True)
	file_url = models.FileField(verbose_name = _("File"), upload_to = file_path)
	file_type = models.ForeignKey(MimeType, verbose_name=_('Type file'), related_name='topic_files')


	class Meta:
		verbose_name = _("File")
		verbose_name_plural = _("Files")
		ordering = ('-id',)

	def __str__(self):
		return self.name