from django.utils.translation import ugettext_lazy as _
from django.db import models
from autoslug.fields import AutoSlugField
from users.models import User
from core.models import Resource
from courses.models import Activity

class Avaliacao(Activity):

    name_avalicao = models.CharField(_('Name'), max_length = 100)
    init_date = models.DateField(_('Begin of Avaliacao Date'))
    end_date = models.DateField(_('End of Avaliacao Date'))

    class Meta:
        #ordering = ('create_date','name')
        verbose_name = _('Avaliacao')
        verbose_name_plural = _('Avaliacoes')

def __str__(self):
    return str(self.name) + str("/") + str(self.topic)
