# coding=utf-8
from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import Pendencies

class PendenciesForm(forms.ModelForm):
	class Meta:
		model = Pendencies
		fields = ['action', 'begin_date', 'end_date']