""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from django import template
from django.utils.translation import ugettext_lazy as _

register = template.Library()

@register.filter(name = 'indicator_description')
def indicator_description(title):
    if title == "access_enviromment":
        return _("Access to the discipline environment")
    elif title == "distincts_days":
        return _("Different days that accessed the discipline")
    elif title == "access_resource":
        return _("Resource access")
    elif title == "distincts_resource":
        return _("Distinct resources accessed")
    elif title == "tasks_on_time":
        return _("Tasks performed on time")
    else:
        return _("Other indicator")