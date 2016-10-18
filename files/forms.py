from django.conf import settings
from django import forms
from .models import TopicFile
from django.core.exceptions import ValidationError, FieldError
from django.utils.translation import ugettext_lazy as _

class FileForm(forms.ModelForm):

	def clean_file_url(self):
		file_url = self.cleaned_data['file_url']
		if file_url._size > settings.MAX_UPLOAD_SIZE:
			raise forms.ValidationError(_('File too large (Max 10MB)'))
		return file_url


	class Meta:
		model = TopicFile
		fields = ['name', 'file_url']

class UpdateFileForm(forms.ModelForm):
	file_url = forms.FileField(required=False)

	def clean_file_url(self):
		file_url = self.cleaned_data['file_url']
		print(file_url)
		if file_url:
			if hasattr(file_url, '_size'):
				if file_url._size > settings.MAX_UPLOAD_SIZE:
					raise forms.ValidationError(_('File too large (Max 10MB)'))
		return file_url


	class Meta:
		model = TopicFile
		fields = ['name', 'file_url']