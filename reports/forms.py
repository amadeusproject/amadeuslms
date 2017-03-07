from django import forms
from django.utils.translation import ugettext_lazy as _
import datetime

class CreateInteractionReportForm(forms.Form):
	topics = forms.ChoiceField(required=True)
	init_date = forms.DateField(required=True)
	end_date = forms.DateField(required=True)

	from_mural = forms.BooleanField()
	from_messages = forms.BooleanField()

