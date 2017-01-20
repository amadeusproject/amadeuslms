from django.db import models
from autoslug.fields import AutoSlugField
from django.utils.translation import ugettext_lazy as _

from topics.models import Resource

class Pendencies(models.Model):
	action = models.CharField(_('Action'), max_length = 100, choices = (("view", _("Visualize")), ("create", _("Create")), ("answer", _("Answer")), ("access", _("Access"))))
	begin_date = models.DateTimeField(_('Begin Date'), null = True, blank = True)
	end_date = models.DateTimeField(_('End Date'), null = True, blank = True)
	resource = models.ForeignKey(Resource, verbose_name = _('Resource'), related_name = 'pendencies_resource', null = True)