# coding=utf-8
from django import forms

from .models import Themes

class BasciElemetsForm(forms.ModelForm):
	
	class Meta:
		model = Themes
		fields = ['title', 'small_logo', 'large_logo', 'footer_note']

class CSSStyleForm(forms.ModelForm):

	class Meta:
		model = Themes
		fields = ['css_style']
		widgets = {
			'css_style': forms.RadioSelect
		}