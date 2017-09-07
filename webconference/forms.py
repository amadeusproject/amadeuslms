# coding=utf-8
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.html import strip_tags
from django.forms.models import inlineformset_factory
import datetime

from subjects.models import Tag
from subjects.forms import ParticipantsMultipleChoiceField

from .models import Webconference, ConferenceSettings

from pendencies.forms import PendenciesForm
from pendencies.models import Pendencies

class WebconferenceForm(forms.ModelForm):
	subject = None
	control_subject = forms.CharField(widget = forms.HiddenInput())
	students = ParticipantsMultipleChoiceField(queryset = None)

	def __init__(self, *args, **kwargs):
		super(WebconferenceForm, self).__init__(*args, **kwargs)

		self.subject = kwargs['initial'].get('subject', None)

		if self.instance.id:
			self.subject = self.instance.topic.subject
			self.initial['tags'] = ", ".join(self.instance.tags.all().values_list("name", flat = True))

		self.initial['control_subject'] = self.subject.id

		self.fields['students'].queryset = self.subject.students.all()
		self.fields['groups'].queryset = self.subject.group_subject.all()

	tags = forms.CharField(label = _('Tags'), required = False)

	class Meta:
		model = Webconference
		fields = ['name', 'presentation', 'start', 'end', 'brief_description', 'all_students', 'students', 'groups', 'show_window', 'visible']
		labels = {
			'name': _('Web Conference Title'),
			'presentation': _('Presentation'),
		}
		widgets = {
			'presentation': forms.Textarea,
			'brief_description': forms.Textarea,
			'students': forms.SelectMultiple,
			'groups': forms.SelectMultiple,
		}

	def clean_name(self):
		name = self.cleaned_data.get('name', '')

		topics = self.subject.topic_subject.all()

		for topic in topics:
			if self.instance.id:
				same_name = topic.resource_topic.filter(name__unaccent__iexact = name).exclude(id = self.instance.id).count()
			else:
				same_name = topic.resource_topic.filter(name__unaccent__iexact = name).count()

			if same_name > 0:
				self._errors['name'] = [_('This subject already has a web conference with this name')]

				return ValueError

		return name


	def clean_start(self):
		start = self.cleaned_data['start']
		if start.date() < datetime.datetime.now().date():
			self._errors['start'] = [_('This date must be today or after')]
			return ValueError

		return start

	def clean_end(self):
		end = self.cleaned_data['end']
		start =  self.cleaned_data['start']

		if start is ValueError or end < start:
			self._errors['end'] = [_('This date must be equal start date/hour or after')]
			return ValueError

		return end

	def save(self, commit = True):
		super(WebconferenceForm, self).save(commit = True)

		self.instance.save()

		previous_tags = self.instance.tags.all()

		tags = self.cleaned_data['tags'].split(",")

        #Excluding unwanted tags
		for prev in previous_tags:
			if not prev.name in tags:
				self.instance.tags.remove(prev)

		for tag in tags:
			tag = tag.strip()

			exist = Tag.objects.filter(name = tag).exists()

			if exist:
				new_tag = Tag.objects.get(name = tag)
			else:
				new_tag = Tag.objects.create(name = tag)

			if not new_tag in self.instance.tags.all():
				self.instance.tags.add(new_tag)

		return self.instance

class WebConferenceUpdateForm(WebconferenceForm):

	def clean_start(self):
		return self.cleaned_data['start']


class SettingsForm(forms.ModelForm):

	class Meta:
		model = ConferenceSettings
		fields = ['domain']

		labels = {
			'domain': _('Domain'),
		}

		help_texts = {
			'domain': _('The domain of the jitsi server, e.g. meet.jit.si'),
		}

InlinePendenciesFormset = inlineformset_factory(Webconference, Pendencies, form = PendenciesForm, extra = 1, max_num = 3, validate_max = True, can_delete = True)
