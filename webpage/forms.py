# coding=utf-8
from django import forms
from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext_lazy as _

from pendencies.forms import PendenciesForm
from pendencies.models import Pendencies

from .models import Webpage

class WebpageForm(forms.ModelForm):
	tags = forms.CharField(label = _('Tags'), required = False)

	class Meta:
		model = Webpage
		fields = ['name', 'content', 'brief_description', 'all_students', 'students', 'groups', 'show_window', 'visible']
		widgets = {
			'content': forms.Textarea,
			'brief_description': forms.Textarea,
			'students': forms.SelectMultiple,
			'groups': forms.SelectMultiple,
		}

InlinePendenciesFormset = inlineformset_factory(Webpage, Pendencies, form = PendenciesForm, extra = 1, can_delete = True)