""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

import random
from datetime import datetime
from django import template
from django.utils import timezone
register = template.Library()

@register.filter('enable_upload')
def enable_upload(begin_date, end_date):
    enable = False

    today = timezone.localtime(timezone.now())

    if timezone.localtime(begin_date).date() < today.date() < timezone.localtime(end_date).date():
        enable = True
    elif timezone.localtime(begin_date).date() == today.date() and timezone.localtime(begin_date).time() <= today.time():
        enable = True
    elif timezone.localtime(end_date).date() == today.date() and today.time() < timezone.localtime(end_date).time():
        enable = True
    
    return enable