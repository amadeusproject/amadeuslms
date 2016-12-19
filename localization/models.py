from django.db import models
from django.utils.translation import ugettext_lazy as _

class Country(models.Model):
	name = models.CharField(_('Name'), max_length = 100)
	shortname = models.CharField(_('Short Name'), max_length = 5)

	class Meta:
		verbose_name = _('Country')
		verbose_name_plural = _('Countries')

	def __str__(self):
		return self.name

class State(models.Model):
	name = models.CharField(_('Name'), max_length = 100)
	shortname = models.CharField(_('Short Name'), max_length = 5)
	country = models.ForeignKey(Country, verbose_name = _('Country'))

	class Meta:
		verbose_name = _('State')
		verbose_name_plural = _('States')

	def __str__(self):
		return self.name

class City(models.Model):
	name = models.CharField(_('Name'), max_length = 100)
	state = models.ForeignKey(State, verbose_name = _('State'))

	class Meta:
		verbose_name = _('City')
		verbose_name_plural = _('Cities')

	def __str__(self):
		return self.name	
