""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from django import template

register = template.Library()

@register.inclusion_tag('pagination.html')
def pagination(request, paginator, page_obj):
    context = {
        'request': request,
        'paginator': paginator,
        'page_obj': page_obj,
    }

    page_numbers = []

    if paginator.num_pages <= 6:
        page_numbers = paginator.page_range
    else:
        init = page_obj.number - 4
        end = page_obj.number + 2

        if init <= 0:
            init = 1

        if end > paginator.num_pages:
            end = paginator.num_pages + 1

        if (end - init) < 6:
            if init == 1 and end < paginator.num_pages:
                end += (6 - (end - init))
            elif init > 1 and end == paginator.num_pages + 1:
                init -= (6 - (end - init))

        for n in range(init, end):
            if n > 0 and n <= paginator.num_pages:
                page_numbers.append(n)

    context['page_numbers'] = page_numbers

    getvars = request.GET.copy()

    if 'page' in getvars:
        del getvars['page']
        
    if len(getvars) > 0:
        context['getvars'] = '&%s' % getvars.urlencode()

    return context