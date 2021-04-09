""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy

from topics.models import Resource
from users.models import User

class H5P(Resource):
    url = models.CharField(_("URL"), max_length=250)
    data_ini = models.DateTimeField(_('Init Date'), auto_now_add = False)
    data_end = models.DateTimeField(_('End Date'), auto_now_add = False)

    class Meta:
        verbose_name = _("H5P")
        verbose_name_plural = _("H5Ps")

    def __str__(self):
        return self.name

    def access_link(self):
        if self.show_window:
            return reverse_lazy(
                "h5p:window_view", args=(), kwargs={"slug": self.slug}
            )

        return reverse_lazy("h5p:view", args=(), kwargs={"slug": self.slug})

    def update_link(self):
        return "h5p:update"

    def delete_link(self):
        return "h5p:delete"

    def delete_message(self):
        return _("Are you sure you want delete this H5P component")

class UserScores(models.Model):
    h5p_component = models.ForeignKey(H5P, verbose_name = _("H5P component"), related_name = 'user_score', null = True)
    student = models.ForeignKey(User, verbose_name = _('User'), related_name = 'h5p_student', null = True)
    max_score = models.DecimalField(max_digits = 5, decimal_places = 2, verbose_name = _('Max Score'))
    score = models.DecimalField(max_digits = 5, decimal_places = 2, verbose_name = _('Student Score'))
    interaction_date = models.DateTimeField(_('Interaction Date'), auto_now_add = True)