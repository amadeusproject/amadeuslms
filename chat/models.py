import os
import time
from django.db import models
from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from subjects.models import Subject
from users.models import User

def validate_img_extension(value):
	valid_formats = ['image/jpeg','image/x-citrix-jpeg','image/png','image/x-citrix-png','image/x-png','image/gif']
	
	if hasattr(value.file, 'content_type'):
		if not value.file.content_type in valid_formats:
			raise ValidationError(_('File not supported.'))

def upload_filename(instance, filename):
	path = "chat/"
	filename = str(int(time.time())) + "_" + filename

	return os.path.join(path, filename)

class Conversation(models.Model):
	user_one = models.ForeignKey(User, verbose_name = _('User One'), related_name = 'talk_user_start')
	user_two = models.ForeignKey(User, verbose_name = _('User Two'), related_name = 'talk_user_end')

class TalkMessages(models.Model):
	text = models.TextField(_('Comment'), blank = True)
	image = models.ImageField(verbose_name = _('Image'), null = True, blank = True, upload_to = upload_filename, validators = [validate_img_extension])
	talk = models.ForeignKey(Conversation, verbose_name = _('Conversation'), related_name = 'message_talk', null = True)
	user = models.ForeignKey(User, verbose_name = _('User'), related_name = 'message_user', null = True)
	subject = models.ForeignKey(Subject, verbose_name = _('Subject'), related_name = 'message_subject', null = True)
	create_date = models.DateTimeField(_('Create Date'), auto_now_add = True)

class ChatVisualizations(models.Model):
	viewed = models.BooleanField(_('Viewed'), default = False)
	message = models.ForeignKey(TalkMessages, verbose_name = _('Message'), related_name = 'chat_visualization_message', null = True)
	user = models.ForeignKey(User, verbose_name = _('User'), related_name = "chat_visualization_user", null = True)
	date_viewed = models.DateTimeField(_('Date/Time Viewed'), null = True, blank = True)

class ChatFavorites(models.Model):
	message = models.ForeignKey(TalkMessages, verbose_name = _('Message'), related_name = 'chat_favorites_message', null = True)
	user = models.ForeignKey(User, verbose_name = _('User'), related_name = "chat_favorites_user", null = True)