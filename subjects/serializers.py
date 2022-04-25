""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

import datetime
from django.db.models import Q

from rest_framework import serializers

from chat.models import ChatVisualizations
from mural.models import MuralVisualizations
from notifications.models import Notification

from .models import Subject, Tag


class TagSerializer(serializers.ModelSerializer):
    def validate(self, data):
        query = Tag.objects.filter(name=data['name'])

        if query.exists():
            data['id'] = query[0].id
        else:
            data['id'] = ""

        return data

    class Meta:
        model = Tag
        fields = '__all__'
        extra_kwargs = {
            "name": {
                "validators": [],
            },
        }
        validators = []


class SubjectSerializer(serializers.ModelSerializer):
    mural = serializers.SerializerMethodField()
    notifications = serializers.SerializerMethodField()
    pendencies = serializers.SerializerMethodField()

    def get_mural(self, subject):
        user = self.context.get("request_user", None)

        if user is not None:
            return MuralVisualizations.objects.filter(Q(user = user) & Q(viewed = False) & (Q(post__subjectpost__space = subject) | Q(comment__post__subjectpost__space = subject))).count()

        return 0

    def get_notifications(self, subject):
        user = self.context.get("request_user", None)

        if user is not None:
            return ChatVisualizations.objects.filter(Q(user=user) & Q(viewed=False) & Q(message__subject=subject)
                                                     & (Q(user__is_staff=True) | Q(message__subject__students=user)
                                                        | Q(message__subject__professor=user)
                                                        | Q(message__subject__category__coordinators=user)))\
                .distinct().count()

        return 0

    def get_pendencies(self, subject):
        user = self.context.get("request_user", None)

        if user is not None:
            return Notification.objects.filter(Q(user = user) & Q(viewed = False) 
                                            & Q(task__resource__topic__subject = subject)
                                            & Q(creation_date = datetime.datetime.now())).count()

        return 0

    class Meta:
        model = Subject
        fields = ["name", "slug", "visible", "description_brief", "description", "subscribe_begin", "subscribe_end", "init_date", "end_date", "price", "notifications", "pendencies", "mural"]