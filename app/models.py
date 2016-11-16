from django.db import models
from django.utils.translation import ugettext_lazy as _
# Create your models here.

class EmailBackend(models.Model):

    SAFE_CONECTIONS = (
        (0, _('No')),
        (1, _('TLS, if available')),
        (2, 'TLS'),
        (3, 'SSL'),

    )
    description = models.CharField(_('Description'), max_length=100)
    host = models.URLField(_('E-mail Host'))
    port = models.CharField(_('Email Port'), max_length=4, blank=True)
    username = models.CharField(_('Email host username'), max_length=30)
    password = models.CharField(_('Email host password'), max_length=30, blank=True)
    safe_conection = models.IntegerField(_('Use safe conection'), choices=SAFE_CONECTIONS, default=0)
    default_from_email = models.EmailField(_('Default from email'))

    class Meta:
        verbose_name = _('Amadeus SMTP setting')
        verbose_name_plural = _('Amadeus SMTP settings')

    def __str__(self):
        return self.username
