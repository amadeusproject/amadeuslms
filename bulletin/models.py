import os
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy

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
			raise ValidationError(_('Please select a valid file. The uploaded file must have one of the following extensions: .doc, .docx, .html, .jpg, .odp, .ods, .odt, .pdf, .png, .ppt, .pptx, .xlx e .xlsx'))

class Bulletin(Resource):
	content = models.TextField(_('Bulletin Content'), blank = True)
	file_content = models.FileField(_('File'), blank = True, upload_to = 'files/', validators = [validate_file_extension])

	class Meta:
		verbose_name = _('Bulletin')
		verbose_name_plural = _('Bulletins')

	def __str__(self):
		return self.name

	def access_link(self):
		if self.show_window:
			return reverse_lazy('bulletin:window_view', args = (), kwargs = {'slug': self.slug})

		return reverse_lazy('bulletin:view', args = (), kwargs = {'slug': self.slug})

	def update_link(self):
		return 'bulletin:update'

	def delete_link(self):
		return 'bulletin:delete'

	def delete_message(self):
		return _('Are you sure you want delete the bulletin')
