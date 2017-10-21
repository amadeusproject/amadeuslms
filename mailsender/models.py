""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""


from django.db import models
from django.utils.translation import ugettext_lazy as _

class MailSender(models.Model):
	description = models.CharField(_('Description'), max_length = 200)
	hostname = models.CharField(_('Host name'), max_length = 200)
	port = models.IntegerField(_('Port Number'))
	username = models.CharField(_('Username'), max_length = 200)
	password = models.CharField(_('Password'), max_length = 256)
	crypto = models.IntegerField(_('Criptografy'), choices = ((1, _('No')), (2, _('SSL')), (3, _('TLS')), (4, _('TLS, if possible'))))

	class Meta:
		verbose_name = _('Mail sender configuration')
		verbose_name_plural = _('Mail sender configurations')

	def __str__(self):
		return self.description
