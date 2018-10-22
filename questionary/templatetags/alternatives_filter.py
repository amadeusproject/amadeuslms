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
register = template.Library()

@register.filter('is_answer')
def is_answer(alt, answer):
    checked = ''

    if answer and alt == answer.id:
        checked = 'checked'

    return checked

@register.filter('shuffle')
def shuffle(alts):
    tmp = list(alts)
    random.shuffle(tmp)
    return tmp

@register.filter('disabled')
def disabled(end_date, has_privileges):
    disabled = ''

    if end_date.date() < datetime.today().date():
        disabled = 'disabled'
    elif end_date.date() == datetime.today().date() and end_date.time() < datetime.today().time():
        disabled = 'disabled'
    elif has_privileges:
        disabled = 'disabled'

    return disabled

@register.filter('view_results')
def view_results(end_date, has_privileges):
    show = False

    if end_date.date() < datetime.today().date():
        show = True
    elif end_date.date() == datetime.today().date() and end_date.time() < datetime.today().time():
        show = True
    elif has_privileges:
        show = True

    return show

@register.filter('veredict')
def veredict(alternative, answer):
    icon = ''

    if answer:
        if answer.id == alternative.id:
            if answer.is_correct:
                icon = 'fa-check correct_answer'
            else:
                icon = 'fa-times wrong_answer'
    
    if alternative.is_correct:
        icon = 'fa-check correct_answer'


    return icon