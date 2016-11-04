from django import forms
from .models import EmailBackend
from django.utils.translation import ugettext_lazy as _

class EmailBackendForm(forms.ModelForm):

	def save(self, commit=True):
		super(EmailBackendForm, self).save()
		print('Saved')
		return self.instance

	class Meta:
		model = EmailBackend
		fields = ('description', 'host', 'port', 'username', 'password', 'safe_conection', 'default_from_email')
		help_texts = {
			'host': _('A host name. Example: smtp.gmail.com'),
			'port': _('A port number'),
			'usermane': _('Your host username'),
			'password': _('Your host password'),
		}
		
    