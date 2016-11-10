from django import forms
from django.core.validators import validate_email
from .models import EmailBackend
from django.utils.translation import ugettext_lazy as _

class EmailBackendForm(forms.ModelForm):
	def clean_default_from_email(self):
		default_email = self.cleaned_data['default_from_email']
		validate_email(default_email)
		return default_email

	class Meta:
		model = EmailBackend
		fields = ('description', 'host', 'port', 'username', 'password', 'safe_conection', 'default_from_email')
		help_texts = {
			'host': _('A host name. Example: smtp.gmail.com'),
			'port': _('A port number'),
			'usermane': _('Your host username'),
			'password': _('Your host password'),
		}
		
    