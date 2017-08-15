import os
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy

from topics.models import Resource

def validate_file_extension(value):
	valid_formats = [
		'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
		'application/vnd.ms-excel','application/vnd.oasis.opendocument.spreadsheet','text/csv'
	]

	if hasattr(value.file, 'content_type'):
		if not value.file.content_type in valid_formats:
			raise ValidationError(_('Please select a valid file. The uploaded file must have one of the following extensions: .csv, .xlx, .xls and .xlsx'))

class Bulletin(Resource):
	content = models.TextField(_('Bulletin Content'), blank = True)
	file_content = models.FileField(_('Goals'), blank = True, upload_to = 'bulletin/goals', validators = [validate_file_extension])
	indicators = models.FileField(_('Relevant Indicators'), blank = True,null = True, upload_to = 'bulletin/indicators', validators = [validate_file_extension])

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
