""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

# coding=utf-8
import datetime

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.formats import get_format
from django.utils import timezone

from subjects.models import Subject

from .models import Pendencies

class PendenciesForm(forms.ModelForm):
	subject = forms.CharField(widget = forms.HiddenInput())

	def __init__(self, *args, **kwargs):
		super(PendenciesForm, self).__init__(*args, **kwargs)

		if kwargs.get('initial', None):
			self.fields['action'].choices = kwargs['initial'].get('actions', [])

		datetime_formats = get_format('DATETIME_INPUT_FORMATS')

		self.fields['begin_date'].input_formats = datetime_formats
		self.fields['end_date'].input_formats = datetime_formats

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
				if not self.instance.id and begin_date.date() < datetime.datetime.today().date():
					self.add_error('begin_date', _("This input should be filled with a date equal or after today's date."))

				if begin_date.date() < subject.init_date:
					self.add_error('begin_date', _('This input should be filled with a date equal or after the subject begin date.("%s")')%(subject.init_date))

				if begin_date.date() > subject.end_date:
					self.add_error('begin_date', _('This input should be filled with a date equal or before the subject end date.("%s")')%(subject.end_date))

			if not end_date == ValueError and end_date:
				if not self.instance.id and end_date.date() < datetime.datetime.today().date():
					self.add_error('end_date', _("This input should be filled with a date equal or after today's date."))

				if end_date.date() < subject.init_date:
					self.add_error('end_date', _('This input should be filled with a date equal or after the subject begin date.("%s")')%(subject.init_date))

				if end_date.date() > subject.end_date:
					self.add_error('end_date', _('This input should be filled with a date equal or before the subject end date.("%s")')%(subject.end_date))

		return cleaned_data

class PendenciesLimitedForm(forms.ModelForm):
	subject = forms.CharField(widget = forms.HiddenInput())

	def __init__(self, *args, **kwargs):
		super(PendenciesLimitedForm, self).__init__(*args, **kwargs)

		if kwargs.get('initial', None):
			self.fields['action'].choices = kwargs['initial'].get('actions', [])

		datetime_formats = get_format('DATETIME_INPUT_FORMATS')

		self.fields['begin_date'].input_formats = datetime_formats
		self.fields['end_date'].input_formats = datetime_formats
		self.fields['limit_date'].input_formats = datetime_formats

	begin_date_check = forms.BooleanField(required = False)
	end_date_check = forms.BooleanField(required = False)
	limit_date_check = forms.BooleanField(required = False)

	class Meta:
		model = Pendencies
		fields = ['action', 'begin_date', 'end_date', 'limit_date']

	def clean(self):
		cleaned_data = super(PendenciesLimitedForm, self).clean()

		pend_id = cleaned_data.get('id', None)

		limit_submission_date = self.data.get('limit_submission_date', None)
		action = cleaned_data.get('action', None)
		begin_date = cleaned_data.get('begin_date', None)
		end_date = cleaned_data.get('end_date', None)
		limit_date = cleaned_data.get('limit_date', None)
		begin_check = cleaned_data.get('begin_date_check', False)
		end_check = cleaned_data.get('end_date_check', False)
		limit_check = cleaned_data.get('limit_date_check', False)
		subject_id = cleaned_data.get('subject', None)

		if begin_check or end_check or limit_date:
			if not action:
				self.add_error('action', _('This field is required.'))

		if not begin_date and begin_check:
			self.add_error('begin_date', _('This field is required.'))

		if not end_date and end_check:
			self.add_error('end_date', _('This field is required.'))

		if not limit_date and limit_check:
			self.add_error('limit_date', _('This field is required.'))

		if begin_date and end_date:
			if not begin_date == ValueError and not end_date == ValueError:
				if begin_date > end_date:
					self.add_error('begin_date', _('This input should be filled with a date equal or before the End Date.'))
					self.add_error('end_date', _('This input should be filled with a date equal or after the Begin Date.'))

		if begin_date and limit_date:
			if not begin_date == ValueError and not limit_date == ValueError:
				if begin_date.date() > limit_date.date():
					self.add_error('begin_date', _('This input should be filled with a date equal or before the Limit Date.'))
					self.add_error('limit_date', _('This input should be filled with a date equal or after the Begin Date.'))

		if end_date and limit_date:
			if not end_date == ValueError and not limit_date == ValueError:
				if end_date.date() > limit_date.date():
					self.add_error('end_date', _('This input should be filled with a date equal or before the Limit Date.'))
					self.add_error('limit_date', _('This input should be filled with a date equal or after the End Date.'))

		if subject_id:
			subject = Subject.objects.get(id = subject_id)

			if not begin_date == ValueError and begin_date:
				if not self.instance.id and begin_date.date() < datetime.datetime.today().date():
					self.add_error('begin_date', _("This input should be filled with a date equal or after today's date."))

				if begin_date.date() < subject.init_date:
					self.add_error('begin_date', _('This input should be filled with a date equal or after the subject begin date.("%s")')%(subject.init_date))

				if begin_date.date() > subject.end_date:
					self.add_error('begin_date', _('This input should be filled with a date equal or before the subject end date.("%s")')%(subject.end_date))

			if not end_date == ValueError and end_date:
				if not self.instance.id and end_date.date() < datetime.datetime.today().date():
					self.add_error('end_date', _("This input should be filled with a date equal or after today's date."))

				if end_date.date() < subject.init_date:
					self.add_error('end_date', _('This input should be filled with a date equal or after the subject begin date.("%s")')%(subject.init_date))

				if end_date.date() > subject.end_date:
					self.add_error('end_date', _('This input should be filled with a date equal or before the subject end date.("%s")')%(subject.end_date))

			if not limit_date == ValueError and limit_date:
				if not self.instance.id and limit_date.date() < datetime.datetime.today().date():
					self.add_error('limit_date', _("This input should be filled with a date equal or after today's date."))

				if limit_date.date() < subject.init_date:
					self.add_error('limit_date', _('This input should be filled with a date equal or after the subject begin date.("%s")')%(subject.init_date))

				if limit_date.date() > subject.end_date:
					self.add_error('limit_date', _('This input should be filled with a date equal or before the subject end date.("%s")')%(subject.end_date))

		if limit_submission_date:
			limit_submission_date = datetime.datetime.strptime(limit_submission_date, get_format('DATETIME_CONVERT_FORMAT'))
			limit_submission_date = timezone.make_aware(limit_submission_date, timezone.get_current_timezone())

			if not begin_date == ValueError and begin_date:
				if begin_date.date() > limit_submission_date.date():
					self.add_error('begin_date', _('This input should be filled with a date equal or before the goals submission limit date.("%s")')%(limit_submission_date.date()))

			if not end_date == ValueError and end_date:
				if end_date.date() > limit_submission_date.date():
					self.add_error('end_date', _('This input should be filled with a date equal or before the goals submission limit date.("%s")')%(limit_submission_date.date()))

			if not limit_date == ValueError and limit_date:
				if limit_date.date() > limit_submission_date.date():
					self.add_error('limit_date', _('This input should be filled with a date equal or before the goals submission limit date.("%s")')%(limit_submission_date.date()))

		return cleaned_data
