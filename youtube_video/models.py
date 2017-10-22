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

class YTVideo(Resource):
	url = models.CharField(_('URL'), max_length = 250)

	class Meta:
		verbose_name = _('YTVideo')
		verbose_name_plural = _('YTVideos')

	def __str__(self):
		return self.name

	def access_link(self):
		if self.show_window:
			return reverse_lazy('youtube:window_view', args = (), kwargs = {'slug': self.slug})

		return reverse_lazy('youtube:view', args = (), kwargs = {'slug': self.slug})

	def update_link(self):
		return 'youtube:update'

	def delete_link(self):
		return 'youtube:delete'

	def delete_message(self):
		return _('Are you sure you want delete the YouTube Video')

	def get_embed_url(self):
		if not "embed" in self.url:
			parts = self.url.split("=")

			if parts[1]:
				return "https://www.youtube.com/embed/" + parts[1]

		return self.url
