""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from django.db import models
from django.utils.translation import ugettext_lazy as _

from users.models import User
from pendencies.models import Pendencies

class Notification(models.Model):
	meta = models.DateTimeField(_('Meta'), null = True, blank = True)
	task = models.ForeignKey(Pendencies, verbose_name = _('Task'), related_name = 'notification_pendencies')
	user = models.ForeignKey(User, verbose_name = _('User'), related_name = 'notification_user')
	level = models.IntegerField(_('Type'), choices = ((1, _('Type 1-A')), (2, _('Type 1-B')), (3, _('Type 2')), (4, _('Type 3'))))
	viewed = models.BooleanField(_('Visualized'), default = False)
	creation_date = models.DateField(_('Creation Date'), auto_now_add = True)

	def __str__(self):
		return self.task.get_action_display() + " " + str(self.task.resource)
