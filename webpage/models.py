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

class Webpage(Resource):
	content = models.TextField(_('Webpage Content'), blank = True)

	class Meta:
		verbose_name = _('WebPage')
		verbose_name_plural = _('WebPages')

	def __str__(self):
		return self.name

	def access_link(self):
		if self.show_window:
			return reverse_lazy('webpages:window_view', args = (), kwargs = {'slug': self.slug})

		return reverse_lazy('webpages:view', args = (), kwargs = {'slug': self.slug})

	def update_link(self):
		return 'webpages:update'

	def delete_link(self):
		return 'webpages:delete'

	def delete_message(self):
		return _('Are you sure you want delete the webpage')
