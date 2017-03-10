from django import forms
from django.utils.translation import ugettext_lazy as _
import datetime



class CreateInteractionReportForm(forms.Form):
	topic = forms.ChoiceField( label= _("Topics to select data from"))
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
		self.subject = initial['subject'] #so we can check date cleaned data
		self.fields['topic'].choices = [(topic.id, topic.name) for topic in topics]
		self.fields['topic'].choices.append((_("All"), _("All")))

	def clean_init_date(self):
		init_date = self.cleaned_data.get('init_date')
		if init_date < self.subject.init_date:
			self._errors['init_date'] = [_('This date should be right or after ' + str(self.subject.init_date) + ', which is when the subject started. ')]
		return init_date

	def clean_end_date(self):
		end_date = self.cleaned_data.get('init_date')
		if end_date > self.subject.init_date:
			self._errors['end_date'] = [_('This date should be right or before ' + str(self.subject.init_date) + ', which is when the subject finishes. ')]
		return end_date