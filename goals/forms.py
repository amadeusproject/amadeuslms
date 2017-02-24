# coding=utf-8
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.forms.models import inlineformset_factory

from subjects.models import Tag

from pendencies.forms import PendenciesLimitedForm
from pendencies.models import Pendencies

from .models import Goals, GoalItem

class GoalsForm(forms.ModelForm):
	subject = None
	control_subject = forms.CharField(widget = forms.HiddenInput())
	
	def __init__(self, *args, **kwargs):
		super(GoalsForm, self).__init__(*args, **kwargs)

		self.subject = kwargs['initial'].get('subject', None)

		if self.instance.id:
			self.subject = self.instance.topic.subject
			self.initial['tags'] = ", ".join(self.instance.tags.all().values_list("name", flat = True))
		
		self.initial['control_subject'] = self.subject.id

	tags = forms.CharField(label = _('Tags'), required = False)
	limit_submission_date = forms.DateTimeField(input_formats = settings.DATETIME_INPUT_FORMATS)

	class Meta:
		model = Goals
		fields = ['name', 'presentation', 'brief_description', 'show_window', 'visible']
		labels = {
			'name': _('Name'),
		}
		widgets = {
			'presentation': forms.Textarea,
			'brief_description': forms.Textarea,
		}

	def clean(self):
		cleaned_data = super(GoalsForm, self).clean()

		topic = cleaned_data.get('topic', None)

		if topic:
			if self.instance.id:
				exist = topic.resource_topic.filter(goals__isnull = False).exclude(id = self.instance.id).exists()
			else:
				exist = topic.resource_topic.filter(goals__isnull = False).exists()

			if exist:
				self.add_error('name', _('There already is another resource with the goals specification for the Topic %s')%(str(topic)))

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

InlinePendenciesFormset = inlineformset_factory(Goals, Pendencies, form = PendenciesLimitedForm, extra = 1, max_num = 3, validate_max = True, can_delete = True)
InlineGoalItemFormset = inlineformset_factory(Goals, GoalItem, form = GoalItemForm, extra = 1, can_delete = True)