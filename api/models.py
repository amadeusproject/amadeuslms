""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from django.db import models

from chat.models import Conversation, TalkMessages
from log.models import Log
from subjects.models import Subject
from users.models import User


class MobileAccessLog(Log):
    pass


class MobileViewParticipants(Log):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)


class MobileConversationLog(Log):
    receiver_user = models.ForeignKey(User, on_delete=models.CASCADE)
    talk = models.ForeignKey(Conversation, on_delete=models.CASCADE)


class SendMessageLog(Log):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    talk = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    receive_user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.ForeignKey(TalkMessages, on_delete=models.CASCADE)
