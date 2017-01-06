from django.db import models
from django.utils.translation import ugettext_lazy as _

class Security(models.Model):
	allow_register = models.BooleanField(_("Don't allow users to self-register"), default = False)
	maintence = models.BooleanField(_("Put system in maintence mode"), default = False)

	class Meta:
		verbose_name = _('Security configuration')
		verbose_name_plural = _('Security configurations')
