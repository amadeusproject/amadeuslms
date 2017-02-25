# coding=utf-8
from django import forms
from datetime import datetime
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.forms.models import inlineformset_factory

from subjects.models import Tag

from pendencies.forms import PendenciesLimitedForm
from pendencies.models import Pendencies

from .models import Goals, GoalItem

class GoalsForm(forms.ModelForm):
	subject = None
	topic = None
	control_subject = forms.CharField(widget = forms.HiddenInput())
	
	def __init__(self, *args, **kwargs):
		super(GoalsForm, self).__init__(*args, **kwargs)

		self.subject = kwargs['initial'].get('subject', None)
		self.topic = kwargs['initial'].get('topic', None)

		if self.instance.id:
			self.subject = self.instance.topic.subject
			self.topic = self.instance.topic
			self.initial['tags'] = ", ".join(self.instance.tags.all().values_list("name", flat = True))
		
		self.initial['control_subject'] = self.subject.id

	tags = forms.CharField(label = _('Tags'), required = False)

	class Meta:
		model = Goals
		fields = ['name', 'presentation', 'limit_submission_date', 'brief_description', 'show_window', 'visible']
		labels = {
			'name': _('Name'),
		}
		widgets = {
			'presentation': forms.Textarea,
			'brief_description': forms.Textarea,
		}

	def clean(self):
		cleaned_data = super(GoalsForm, self).clean()

		limit_submission_date = cleaned_data.get('limit_submission_date', None)

		if self.topic:
			if self.instance.id:
				exist = self.topic.resource_topic.filter(goals__isnull = False).exclude(id = self.instance.id).exists()
			else:
				exist = self.topic.resource_topic.filter(goals__isnull = False).exists()

			if exist:
				self.add_error('name', _('There already is another resource with the goals specification for the Topic %s')%(str(self.topic)))

		if limit_submission_date:
			if not limit_submission_date == ValueError:
				if not self.instance.id and limit_submission_date.date() < datetime.today().date():
					self.add_error('limit_submission_date', _("This input should be filled with a date equal or after today's date."))

				if limit_submission_date.date() < self.subject.init_date:
					self.add_error('limit_submission_date', _('This input should be filled with a date equal or after the subject begin date.'))

				if limit_submission_date.date() > self.subject.end_date:
					self.add_error('limit_submission_date', _('This input should be filled with a date equal or after the subject end date.'))

		return cleaned_data

	def save(self, commit = True):
		super(GoalsForm, self).save(commit = True)

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

class GoalItemForm(forms.ModelForm):
	class Meta:
		model = GoalItem
		fields = ['description', 'ref_value']

	def clean(self):
		cleaned_data = super(GoalItemForm, self).clean()

		description = cleaned_data.get('description', None)
		ref_value = cleaned_data.get('ref_value', None)

		if ref_value and ref_value != "0":
			if not description:
				self.add_error('description', _('This field is required.'))

		return cleaned_data


InlinePendenciesFormset = inlineformset_factory(Goals, Pendencies, form = PendenciesLimitedForm, extra = 1, max_num = 3, validate_max = True, can_delete = True)
InlineGoalItemFormset = inlineformset_factory(Goals, GoalItem, form = GoalItemForm, extra = 1, can_delete = True)