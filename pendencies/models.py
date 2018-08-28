""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from django.db import models
from autoslug.fields import AutoSlugField
from django.utils.translation import ugettext_lazy as _

from topics.models import Resource

class Pendencies(models.Model):
	action = models.CharField(_('Action'), max_length = 100, choices = (("view", _("Visualize")), ("create", _("Create")), ("answer", _("Answer")), ("access", _("Access")), ("participate", _("Participate")), ("finish", _("Finish")), ("submit", _("Submit"))), blank = True)
	begin_date = models.DateTimeField(_('Begin Date'), null = True, blank = True)
	end_date = models.DateTimeField(_('End Date'), null = True, blank = True)
	limit_date = models.DateTimeField(_('Limit Date'), null = True, blank = True)
	resource = models.ForeignKey(Resource, verbose_name = _('Resource'), related_name = 'pendencies_resource', null = True)
