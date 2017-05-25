# coding=utf-8
from django import forms

from .models import Security

class SecurityForm(forms.ModelForm):
	
	class Meta:
		model = Security
		fields = ['allow_register', 'maintence']		