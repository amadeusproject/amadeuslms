import os
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from topics.models import Resource

def validate_file_extension(value):
	valid_formats = [
		'image/jpeg','image/x-citrix-jpeg','image/png','image/x-citrix-png','image/x-png',
		'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
		'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
		'application/vnd.openxmlformats-officedocument.presentationml.slideshow',
		'application/vnd.openxmlformats-officedocument.presentationml.presentation',
		'application/vnd.ms-excel','text/html','application/msword','application/vnd.oasis.opendocument.presentation',
		'application/vnd.oasis.opendocument.spreadsheet','application/vnd.oasis.opendocument.text',
		'application/pdf'
	]
	
	if hasattr(value.file, 'content_type'):
		if not value.file.content_type in valid_formats:
			raise ValidationError(_('File not supported.'))

class FileLink(Resource):
	file_content = models.FileField(_('File'), blank = True, upload_to = 'files/', validators = [validate_file_extension])

	class Meta:
		verbose_name = _('File Link')
		verbose_name_plural = _('File Links')

	@property
	def filename(self):
		return os.path.basename(self.file_content.name)

	def __str__(self):
		return self.name

	def access_link(self):
		return 'file_links:download'

	def update_link(self):
		return 'file_links:update'

	def delete_link(self):
		return 'file_links:delete'

	def delete_message(self):
		return _('Are you sure you want delete the file link')
