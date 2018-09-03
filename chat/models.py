""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

import os
import time
from os import path
from django.db import models
from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from datetime import timezone

from subjects.models import Subject
from users.models import User

valid_formats = ['image/jpeg','image/x-citrix-jpeg','image/png','image/x-citrix-png','image/x-png','image/gif']

def validate_img_extension(value):
	if hasattr(value.file, 'content_type'):
		if not value.file.content_type in valid_formats:
			raise ValidationError(_('Select a valid file. The file must posses one of this extensions: .jpg, .png, .gif'))

def upload_filename(instance, filename):
	path = "chat/"
	filename = str(int(time.time())) + "_" + filename

	return os.path.join(path, filename)

class Conversation(models.Model):
	user_one = models.ForeignKey(User, verbose_name = _('User One'), related_name = 'talk_user_start')
	user_two = models.ForeignKey(User, verbose_name = _('User Two'), related_name = 'talk_user_end')

class TalkMessages(models.Model):
	text = models.TextField(_('Message'), blank = True)
	image = models.ImageField(verbose_name = _('Image'), null = True, blank = True, upload_to = upload_filename, validators = [validate_img_extension])
	talk = models.ForeignKey(Conversation, verbose_name = _('Conversation'), related_name = 'message_talk', null = True)
	user = models.ForeignKey(User, verbose_name = _('User'), related_name = 'message_user', null = True)
	subject = models.ForeignKey(Subject, verbose_name = _('Subject'), related_name = 'message_subject', null = True)
	create_date = models.DateTimeField(_('Create Date'), auto_now_add = True)

	def get_timestamp(self):
		return str(self.create_date.replace(tzinfo = timezone.utc).timestamp())

	@property
	def image_url(self):
		if self.image and hasattr(self.image, 'url'):
			if path.exists(self.image.path):
				return self.image.url
		
		return ""

class ChatVisualizations(models.Model):
	viewed = models.BooleanField(_('Viewed'), default = False)
	message = models.ForeignKey(TalkMessages, verbose_name = _('Message'), related_name = 'chat_visualization_message', null = True)
	user = models.ForeignKey(User, verbose_name = _('User'), related_name = "chat_visualization_user", null = True)
	date_viewed = models.DateTimeField(_('Date/Time Viewed'), null = True, blank = True)

class ChatFavorites(models.Model):
	message = models.ForeignKey(TalkMessages, verbose_name = _('Message'), related_name = 'chat_favorites_message', null = True)
	user = models.ForeignKey(User, verbose_name = _('User'), related_name = "chat_favorites_user", null = True)