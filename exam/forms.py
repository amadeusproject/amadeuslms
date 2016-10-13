from django.utils.translation import ugettext_lazy as _
from django import forms
from .models import Exam

class ExamForm(forms.ModelForm):
	def clean_end_date(self):
		begin_date = self.data['begin_date']
		limit_date = self.data['limit_date']

		if begin_date and limit_date and limit_date < begin_date:
			raise forms.ValidationError(_('The end date may not be before the start date.'))
		return endDate


	class Meta:
		model = Exam
		fields = ['name','begin_date','limit_date']

		widgets = {
			'name': forms.TextInput(attrs={'placeholder': 'Exam?'}),
			'begin_date': forms.DateTimeInput(attrs={'placeholder': _('Start date to resolve the exam')}),
			'limit_date': forms.DateTimeInput(attrs={'placeholder': _('Finish date permited to resolve the exam')}),
			}
