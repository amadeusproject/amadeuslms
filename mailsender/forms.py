# coding=utf-8
from django import forms

from .models import MailSender

class MailSenderForm(forms.ModelForm):
	
	class Meta:
		model = MailSender
		fields = ['description', 'hostname', 'port', 'username', 'password', 'crypto']
		widgets = {
			'password': forms.PasswordInput(render_value = True)
		}