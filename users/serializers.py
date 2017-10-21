""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

import os
import zipfile
import time
from django.db.models import Q
from django.conf import settings
from django.core.files import File

from rest_framework import serializers

from log.serializers import LogSerializer
from log.models import Log

from chat.models import Conversation, ChatVisualizations

from .models import User

class UserBackupSerializer(serializers.ModelSerializer):
	log = LogSerializer(many = True, source = 'get_items')
	image = serializers.CharField(required = False, allow_blank = True, max_length = 255)

	def validate(self, data):
		user = User.objects.filter(email = data["email"])
		
		if user.exists():
			log = data["get_items"]
			data = user[0].__dict__
			data["get_items"] = log
		else:
			data["id"] = ""

		files = self.context.get('files', None)
		
		if files:
			if data["image"] in files.namelist(): 
				file_path = os.path.join(settings.MEDIA_ROOT, data["image"])

				if os.path.isfile(file_path):
					dst_path = os.path.join(settings.MEDIA_ROOT, "tmp")

					path = files.extract(data["image"], dst_path)

					new_name = os.path.join("users","img_" + str(time.time()) + os.path.splitext(data["image"])[1])

					os.rename(os.path.join(dst_path, path), os.path.join(settings.MEDIA_ROOT, new_name))
					
					data["image"] = new_name
				else:
					path = files.extract(data["image"], settings.MEDIA_ROOT)
			else:
				data["image"] = None

		return data

	class Meta:
		model = User
		fields = '__all__'
		extra_kwargs = {
        	"email": {
	            "validators": [],
	        },
	    }
		validators = []

class UserSerializer(serializers.ModelSerializer):
	unseen_msgs = serializers.SerializerMethodField()

	def get_unseen_msgs(self, user_to):
		user = self.context.get('request_user', None)

		if not user is None:
			chat = Conversation.objects.filter((Q(user_one__email = user) & Q(user_two = user_to)) | (Q(user_one = user_to) & Q(user_two__email = user)))

			if chat.count() > 0:
				chat = chat[0]
				
				return ChatVisualizations.objects.filter(message__talk = chat, user__email = user, viewed = False).count()

		return 0

	class Meta:
		model = User
		fields = ('username','email','image_url','last_update','date_created','last_name','social_name',
			'is_staff','is_active','description','unseen_msgs')
