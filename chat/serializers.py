""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from rest_framework import serializers

from django.db.models import Q

from .models import TalkMessages, ChatFavorites

from subjects.serializers import SubjectSerializer
from users.serializers import UserSerializer

class ChatSerializer(serializers.ModelSerializer):
	user = UserSerializer()
	subject = SubjectSerializer()
	favorite = serializers.SerializerMethodField()

	def get_favorite(self, message):
		user = self.context.get("request_user", None)

		if not user is None:
			return ChatFavorites.objects.filter(Q(user = user) & Q(message = message)).exists()

		return False

	class Meta:
		model = TalkMessages
		fields = ('text', 'user', 'subject', 'image_url', 'create_date', 'favorite', 'id')
