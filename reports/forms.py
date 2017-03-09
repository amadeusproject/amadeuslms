from django import forms
from django.utils.translation import ugettext_lazy as _
import datetime



class CreateInteractionReportForm(forms.Form):
	topic = forms.ChoiceField( label= _("topics to select data from"))
	init_date = forms.DateField()
	end_date = forms.DateField()

	from_mural = forms.BooleanField(required=False)
	from_messages = forms.BooleanField(required=False)

	class Meta:
		fields = ('topic', 'init_date', 'end_date', 'from_mural' , 'from_messages')

	def __init__(self, *args, **kwargs):
		super(CreateInteractionReportForm, self).__init__(*args, **kwargs)
		
		initial = kwargs['initial']
		topics = list(initial['topic'])
		
		self.fields['topic'].choices = [(topic.id, topic.name) for topic in topics]
		self.fields['topic'].choices.append((_("all"), _("all")))
