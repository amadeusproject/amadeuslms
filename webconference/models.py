""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from django.db import models
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from categories.models import Category
from log.models import Log
from subjects.models import Subject
from topics.models import Resource, Topic


class Webconference(Resource):
    presentation = models.TextField(_('Presentation'), blank=True)
    start = models.DateTimeField(_('Start date/hour'))
    end = models.DateTimeField(_('End date/hour'))

    class Meta:
        verbose_name = _('Web Conference')
        verbose_name_plural = _('Web Conferences')

    def __str__(self):
        return self.name

    def access_link(self):
        if self.show_window:
            return reverse_lazy('webconferences:window_view', args=(), kwargs={'slug': self.slug})

        return reverse_lazy('webconferences:view', args=(), kwargs={'slug': self.slug})

    def update_link(self):
        return 'webconferences:update'

    def delete_link(self):
        return 'webconferences:delete'

    def delete_message(self):
        return _('Are you sure you want delete the web conference')


class ConferenceSettings(models.Model):
    domain = models.CharField(_("Domain"), max_length=100, blank=False, null=False)

    class Meta:
        verbose_name = _("Web Conference Setting")
        verbose_name_plural = _("Web Conferences Setting")

    def __str__(self):
        return self.domain


class ViewWebConferenceLog(Log):
    webconference = models.ForeignKey(Webconference, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)


class InitWebConferenceLog(Log):
    webconference = models.ForeignKey(Webconference, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)


class CreateWebConferenceLog(Log):
    webconference = models.ForeignKey(Webconference, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)


class UpdateWebConferenceLog(Log):
    webconference = models.ForeignKey(Webconference, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)


class DeleteWebConferenceLog(Log):
    webconference = models.ForeignKey(Webconference, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)


class ViewStatisticsConferenceLog(Log):
    webconference = models.ForeignKey(Webconference, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)


class SendMessageInWebConferenceLog(Log):
    webconference = models.ForeignKey(Webconference, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    message = models.TextField()


class InsideViewWebConferenceLog(Log):
    webconference = models.ForeignKey(Webconference, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)


class ParticipatingInWebConferenceLog(Log):
    webconference = models.ForeignKey(Webconference, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)


class EndParticipationInConferenceLog(Log):
    webconference = models.ForeignKey(Webconference, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
