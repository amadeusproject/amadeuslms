""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

import re

from os import path
from django.db import models
from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin
from django.contrib.staticfiles.templatetags.staticfiles import static

from log.models import Log

def validate_img_extension(value):
	valid_formats = ['image/jpeg','image/x-citrix-jpeg','image/png','image/x-citrix-png','image/x-png']
	
	if hasattr(value.file, 'content_type'):
		if not value.file.content_type in valid_formats:
			raise ValidationError(_('File not supported.'))

class User(AbstractBaseUser, PermissionsMixin):

	email = models.EmailField(_('Mail'), unique = True, validators = [
			validators.RegexValidator(
				re.compile('^[\w.@+-]+$'),
				_('Type a valid email. This fields should only contain letters, numbers and the characteres: @/./+/-/_ .')
				, 'invalid'
			)
		], help_text = _('Your email address that will be used to access the platform'))
	username = models.CharField(_('Name'), max_length = 100)
	last_name = models.CharField(_('Last Name'), max_length = 100)
	social_name = models.CharField(_('Social Name'), max_length = 100, blank = True, null = True)
	description = models.TextField(_('Description'), blank = True)
	image = models.ImageField(verbose_name = _('Photo'), null=True, blank = True, upload_to = 'users/', validators = [validate_img_extension])
	date_created = models.DateTimeField(_('Create Date'), auto_now_add = True)
	last_update = models.DateTimeField(_('Last Update'), auto_now = True)
	show_email = models.IntegerField(_('Show email?'), null = True, blank = True, choices = ((1, _('Allow everyone to see my address')), (2, _('Only classmates can see my address')), (3, _('Nobody can see my address'))), default = 1)
	is_staff = models.BooleanField(_('Administrator'), default = False)
	is_active = models.BooleanField(_('Active'), default = True)

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['username', 'last_name']

	objects = UserManager()

	class Meta:
		verbose_name = _('User')
		verbose_name_plural = _('Users')

	def __str__(self):
		return self.social_name or (self.username + " " + self.last_name)

	def get_short_name(self):
		return str(self)

	@property
	def image_url(self):
		if self.image and hasattr(self.image, 'url'):
			if path.exists(self.image.path):
				return self.image.url
		
		return static('img/no_image.jpg')

	def get_items(self):
		data = Log.objects.filter(user_id = self.id)

		return data

	def is_admin(self):
		if self.is_staff:
			return _('Yes')

		return _('Is not an admin')
