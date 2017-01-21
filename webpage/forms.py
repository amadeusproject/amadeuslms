# coding=utf-8
from django import forms
from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext_lazy as _
from django.utils.html import strip_tags

from pendencies.forms import PendenciesForm
from pendencies.models import Pendencies

from subjects.models import Tag

from .models import Webpage

class WebpageForm(forms.ModelForm):
	subject = None
	control_subject = forms.CharField(widget = forms.HiddenInput())

	def __init__(self, *args, **kwargs):
		super(WebpageForm, self).__init__(*args, **kwargs)

		self.subject = kwargs['initial'].get('subject', None)
		
		if self.instance.id:
			self.subject = self.instance.subject
			self.initial['tags'] = ", ".join(self.instance.tags.all().values_list("name", flat = True))

		self.initial['control_subject'] = self.subject.id
		
		self.fields['students'].queryset = self.subject.students.all()
		self.fields['groups'].queryset = self.subject.group_subject.all()

	tags = forms.CharField(label = _('Tags'), required = False)

	class Meta:
		model = Webpage
		fields = ['name', 'content', 'brief_description', 'all_students', 'students', 'groups', 'show_window', 'visible']
		labels = {
			'name': _('Webpage name'),
			'content': _('Webpage content'),
		}
		widgets = {
			'content': forms.Textarea,
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
				self._errors['name'] = [_('This subject already has a webpage with this name')]

				return ValueError

		return name

	def clean_content(self):
		content = self.cleaned_data.get('content', '')
		content = strip_tags(content)
		
		if content == '':
			self._errors['content'] = [_('This field is required.')]

			return ValueError

		return content

	def save(self, commit = True):
		super(WebpageForm, self).save(commit = True)

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

InlinePendenciesFormset = inlineformset_factory(Webpage, Pendencies, form = PendenciesForm, extra = 1, can_delete = True)