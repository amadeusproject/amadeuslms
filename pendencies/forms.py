# coding=utf-8
import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _

from subjects.models import Subject

from .models import Pendencies

class PendenciesForm(forms.ModelForm):
	subject = forms.CharField(widget = forms.HiddenInput())

	def __init__(self, *args, **kwargs):
		super(PendenciesForm, self).__init__(*args, **kwargs)
		
	begin_date_check = forms.BooleanField(required = False)
	end_date_check = forms.BooleanField(required = False)

	class Meta:
		model = Pendencies
		fields = ['action', 'begin_date', 'end_date']

	def clean(self):
		cleaned_data = super(PendenciesForm, self).clean()

		pend_id = cleaned_data.get('id', None)

		action = cleaned_data.get('action', None)
		begin_date = cleaned_data.get('begin_date', None)
		end_date = cleaned_data.get('end_date', None)
		begin_check = cleaned_data.get('begin_date_check', False)
		end_check = cleaned_data.get('end_date_check', False)
		subject_id = cleaned_data.get('subject', None)

		if begin_check or end_check:
			if not action:
				self.add_error('action', _('This field is required.'))

		if not begin_date and begin_check:
			self.add_error('begin_date', _('This field is required.'))

		if not end_date and end_check:
			self.add_error('end_date', _('This field is required.'))

		if begin_date and end_date:
			if not begin_date == ValueError and not end_date == ValueError:
				if begin_date > end_date:
					self.add_error('begin_date', _('This input should be filled with a date equal or before the End Date.'))
					self.add_error('end_date', _('This input should be filled with a date equal or after the Begin Date.'))

		if subject_id:
			subject = Subject.objects.get(id = subject_id)

			if not begin_date == ValueError and begin_date:
				if not pend_id and begin_date.date() < datetime.datetime.today().date():
					self.add_error('begin_date', _("This input should be filled with a date equal or after today's date."))

				if begin_date.date() < subject.init_date:
					self.add_error('begin_date', _('This input should be filled with a date equal or after the subject begin date.'))

				if begin_date.date() > subject.end_date:
					self.add_error('begin_date', _('This input should be filled with a date equal or after the subject end date.'))

			if not end_date == ValueError and end_date:
				if not pend_id and end_date.date() < datetime.datetime.today().date():
					self.add_error('end_date', _("This input should be filled with a date equal or after today's date."))

				if end_date.date() < subject.init_date:
					self.add_error('end_date', _('This input should be filled with a date equal or after the subject begin date.'))

				if end_date.date() > subject.end_date:
					self.add_error('end_date', _('This input should be filled with a date equal or before the subject end date.'))

		return cleaned_data
