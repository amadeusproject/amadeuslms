from django import forms
from .models import Exam

class ExamForm(forms.ModelForm):
	def clean_end_date(self):
		beginDate = self.data['beginDate']
		endDate = self.data['endDate']

		if beginDate and endDate and endDate < beginDate:
			raise forms.ValidationError(_('The end date may not be before the start date.'))
		return endDate

	def clean_begin_date(self):
		endDate = self.data['endDate']
		beginDate = self.data['beginDate']

		if enDate and benginDate and beginDate <= endDate:
			raise forms.ValidationError(_('The exam start date must be after the end of registration.'))
		return beginDate

	def clean_end_date(self):
		beginDate = self.data['beginDate']
		endDate = self.data['endDate']

		if beginDate and endDate and endDate < beginDate:
			raise forms.ValidationError(_('The finish date may not be before the start date.'))
		return end_date



	class Meta:
		model = Exam
		fields = ['name','beginDate','endDate']

		widgets = {
			'name': forms.TextInput(attrs={'placeholder': 'Exam?'}),
			'beginDate': forms.DateTimeInput(attrs={'placeholder': 'Start date to resolve the exam'}),
			'endDate': forms.DateTimeInput(attrs={'placeholder': 'Finish date permited to resolve the exam'}),
			}
