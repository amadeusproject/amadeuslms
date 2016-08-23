import re

from django.db import models
from django.core import validators
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin

class User(AbstractBaseUser, PermissionsMixin):

	username = models.CharField(_('Login'), max_length = 35, unique = True, validators = [
			validators.RegexValidator(
				re.compile('^[\w.@+-]+$'),
				_('Type a valid username. This fields should only contain letters, numbers and the characteres: @/./+/-/_ .')
				, 'invalid'
			)
		], help_text = _('A short name that will be used to identify you in the platform and to access it'))
	email = models.EmailField(_('Mail'), unique = True)
	name = models.CharField(_('Name'), max_length = 100, blank = True)
	city = models.CharField(_('City'), max_length = 90, blank = True)
	state = models.CharField(_('State'), max_length = 30, blank = True)
	gender = models.CharField(_('Gender'), max_length = 1, choices = (('M', _('Male')), ('F', _('Female'))))
	image = models.ImageField(verbose_name = _('Image'), blank = True, upload_to = 'users/', default = 'no_image.jpg')
	birth_date = models.DateField(_('Birth Date'), null = True, blank = True)
	phone = models.CharField(_('Phone'), max_length = 30, blank = True)
	cpf = models.CharField(_('Cpf'), max_length = 15, blank = True)
	type_profile = models.IntegerField(_('Type'), null = True, blank = True, choices = ((1, _('Professor')), (2, _('Student'))))
	date_created = models.DateTimeField(_('Create Date'), auto_now_add = True)
	is_staff = models.BooleanField(_('Administrador'), default = False)
	is_active = models.BooleanField(_('Active'), default = True)

	USERNAME_FIELD = 'username'
	REQUIRED_FIELDS = ['email']

	objects = UserManager()

	class Meta:
		verbose_name = _('User')
		verbose_name_plural = _('Users')

	def __str__(self):
		return self.name or self.username

	def det_full_name(self):
		return str(self)

	def get_short_name(self):
		return str(self).split(" ")[0]