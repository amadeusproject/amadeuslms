""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""


from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils.translation import ugettext_lazy as _

class Log(models.Model):
	component = models.TextField(_('Component (Module / App)'))
	context = JSONField(_('Context'), blank = True)
	action = models.TextField(_('Action'))
	resource = models.TextField(_('Resource'))
	user = models.CharField(_('Actor'), max_length = 100)
	user_id = models.IntegerField(_('Actor id'))
	user_email = models.EmailField(_('Actor Mail'))
	datetime = models.DateTimeField(_("Date and Time of action"), auto_now_add = True)

	class Meta:
		verbose_name = _('Log')
		verbose_name_plural = _('Logs')

	def __str__(self):
		return str(self.user) + ' / ' + self.component