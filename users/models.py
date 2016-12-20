import re

from django.db import models
from django.core import validators
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin
from django.contrib.staticfiles.templatetags.staticfiles import static

class User(AbstractBaseUser, PermissionsMixin):

	email = models.EmailField(_('Mail'), unique = True, validators = [
			validators.RegexValidator(
				re.compile('^[\w.@+-]+$'),
				_('Type a valid username. This fields should only contain letters, numbers and the characteres: @/./+/-/_ .')
				, 'invalid'
			)
		], help_text = _('Your email address that will be used to access the platform'))
	username = models.CharField(_('Name'), max_length = 100)
	last_name = models.CharField(_('Last Name'), max_length = 100)
	social_name = models.CharField(_('Social Name'), max_length = 100, blank = True, null = True)
	description = models.TextField(_('Description'), blank = True)
	image = models.ImageField(verbose_name = _('Photo'), null=True, blank = True, upload_to = 'users/')
	type_profile = models.IntegerField(_('Type'), null = True, blank = True, choices = ((1, _('Professor')), (2, _('Student')), (3, _('Coordinator'))))
	date_created = models.DateTimeField(_('Create Date'), auto_now_add = True)
	show_email = models.IntegerField(_('Show email?'), null = True, choices = ((1, _('Allow everyone to see my address')), (2, _('Only classmates can see my address')), (3, _('Nobody can see my address'))))
	is_staff = models.BooleanField(_('Administrator'), default = False)
	is_active = models.BooleanField(_('Active'), default = True)

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['username', 'last_name']

	objects = UserManager()

	class Meta:
		verbose_name = _('User')
		verbose_name_plural = _('Users')

	def __str__(self):
		return self.social_name or self.username

	def save(self, *args, **kwargs):
		if not self.is_staff and self.type_profile is None:
			self.type_profile = 2

		super(User, self).save(*args, **kwargs)

	@property
	def image_url(self):
		if self.image and hasattr(self.image, 'url'):
			return self.image.url
		else:
			return static('img/no_image.jpg')
