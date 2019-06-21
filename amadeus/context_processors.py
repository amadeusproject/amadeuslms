""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from datetime import datetime

from chat.models import ChatVisualizations
from mural.models import MuralVisualizations
from notifications.models import Notification
from themes.models import Themes


def theme(request):
    def setup_context(context_dict, theme_obj, request_obj):
        context_dict['theme'] = theme_obj
        if "contrast_check" in request_obj.COOKIES.keys():
            context_dict['contrast_cookie'] = True
        else:
            context_dict['contrast_cookie'] = False
        return context_dict

    context = {}

    if Themes.objects.filter(id=1).exists():
        theme = Themes.objects.get(id=1)
        return setup_context(context, theme, request)
    else:
        default_theme = Themes(title="Projeto Amadeus", css_style="green")
        default_theme.save()
        return setup_context(context, default_theme, request)
    return context


def notifies(request):
    context = {}

    notifications = 0

    if request.user.is_authenticated:
        notifications = Notification.objects.filter(creation_date=datetime.now(), viewed=False,
                                                    user=request.user).count()

    context['notifications_count'] = notifications

    return context


def mural_notifies(request):
    context = {}

    notifications = 0

    if request.user.is_authenticated:
        notifications = MuralVisualizations.objects.filter(viewed=False, user=request.user).count()

    context['mural_notifications_count'] = notifications

    return context


def chat_notifies(request):
    context = {}

    notifications = 0

    if request.user.is_authenticated:
        notifications = ChatVisualizations.objects.filter(viewed=False, user=request.user).count()

    context['chat_notifications_count'] = notifications

    return context
