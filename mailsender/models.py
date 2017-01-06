from django.db import models
from django.utils.translation import ugettext_lazy as _

class MailSender(models.Model):
	description = models.CharField(_('Description'), max_length = 200)
	hostname = models.CharField(_('Host name'), max_length = 200)
	port = models.IntegerField(_('Port Number'))
	username = models.CharField(_('Username'), max_length = 200)
	password = models.CharField(_('Password'), max_length = 256)
	crypto = models.IntegerField(_('Criptografy'), choices = ((1, _('No')), (2, _('SSL')), (3, _('TLS')), (4, _('TLS, if possible'))))

	class Meta:
		verbose_name = _('Mail sender configuration')
		verbose_name_plural = _('Mail sender configurations')

	def __str__(self):
		return self.description
