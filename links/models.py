from django.db import models
from courses.models import Material
from autoslug.fields import AutoSlugField
# Create your models here.
class Link(Material):
	link_url = models.URLField()
	link_description = models.CharField(max_length=200)
	class Meta:
		verbose_name = 'Link'
		verbose_name_plural = "Links"
	def __str__(self):
		return str(self.name)
