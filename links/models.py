""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""


from django.db import models
from django.utils.translation import ugettext_lazy as _
from autoslug.fields import AutoSlugField

import datetime
from topics.models import Topic, Resource
from users.models import User
from django.utils import timezone
from django.core.urlresolvers import reverse_lazy

# Create your models here.
class Link(Resource):
    link_url = models.CharField( _("Link_URL"),max_length=250 )


    class Meta:
        verbose_name = "Link"
        verbose_name_plural = "Links"

    def __str__(self):
        return self.name

    def access_link(self):
        return reverse_lazy('links:view', kwargs = {'slug': self.slug})

    def update_link(self):
        return 'links:update'

    def delete_link(self):
        return 'links:delete'

    def delete_message(self):
        return _('Are you sure you want delete the Website link')
