from django.db import models
from courses.models import Material
# Create your models here.
class Link(models.Model):
	name = models.CharField(max_length=100)
	link = models.URLField()
	description = models.CharField(max_length=200)
	class Meta:
		verbose_name = 'Link'
		verbose_name_plural = "Links"
	def __str__(self):
		return str(self.name)
