from django import forms
from .models import TopicFile
from django.utils.translation import ugettext_lazy as _

class FileForm(forms.ModelForm):

	class Meta:
		model = TopicFile
		fields = ['name', 'file_url']