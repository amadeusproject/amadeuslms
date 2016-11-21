from django.db import models
from courses.models import Material
from autoslug.fields import AutoSlugField
from django.utils.translation import ugettext_lazy as _

# Create your models here.
class Link(Material):
	link_url = models.URLField(verbose_name = _("Link_URL"))
	link_description = models.CharField(_('Description'),max_length=200)
	image = models.ImageField(upload_to = 'links/',blank = True)
	class Meta:
		verbose_name = 'Link'
		verbose_name_plural = "Links"
	def __str__(self):
		return str(self.name)
