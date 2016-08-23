from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import Subscribe

class SubscribeForm(forms.ModelForm):
	class Meta:
		model = Subscribe
		fields = ['user', 'course']