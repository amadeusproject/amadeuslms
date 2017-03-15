from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy

from topics.models import Resource

class Webconference(Resource):
    presentation = models.TextField(_('Presentation'), blank = True)
    start = models.DateTimeField(_('Start date/hour'))
    end = models.DateTimeField(_('End date/hour'))

    class Meta:
        verbose_name = _('Web Conference')
        verbose_name_plural = _('Web Conferences')

    def __str__(self):
        return self.name

    def access_link(self):
        if self.show_window:
            return reverse_lazy('webconferences:window_view', args = (), kwargs = {'slug': self.slug})

        return reverse_lazy('webconferences:view', args = (), kwargs = {'slug': self.slug})

    def update_link(self):
        return 'webconferences:update'

    def delete_link(self):
        return 'webconferences:delete'

    def delete_message(self):
        return _('Are you sure you want delete the web conference')
