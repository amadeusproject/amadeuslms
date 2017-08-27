# coding=utf-8
from django import forms
from django.utils.translation import ugettext_lazy as _

from subjects.models import Subject

from .models import Topic

class TopicForm(forms.ModelForm):
	subject = None

	def __init__(self, *args, **kwargs):
		super(TopicForm, self).__init__(*args, **kwargs)

		self.subject = kwargs['initial'].get('subject', None)

		if self.instance and self.instance.id:
			if self.instance.repository:
				self.fields['name'].widget.attrs['readonly'] = True


	def clean_repository(self):
		repository = self.cleaned_data.get('repository', False)

		if not self.instance.id:
			if repository:
				has_repo = self.subject.topic_subject.filter(repository = True).exists()

				if has_repo:
					self._errors['repository'] = [_('This subject already has a repository')]

					return ValueError

		return repository

	def clean_name(self):
		name = self.cleaned_data.get('name', '')
		repo = self.cleaned_data.get('repository', False)

		if self.instance.id:
			same_name = self.subject.topic_subject.filter(name__unaccent__iexact = name).exclude(id = self.instance.id).count()
		else:
			same_name = self.subject.topic_subject.filter(name__unaccent__iexact = name).count()

		if same_name > 0:
			if repo:
				self._errors['name'] = [_('This subject already has a repository')]
			else:
				self._errors['name'] = [_('This subject already has a topic with this name')]

			return ValueError

		return name

	class Meta:
		model = Topic
		fields = ['repository', 'name', 'description', 'visible' ]
		widgets = {
			'description': forms.Textarea,
		}
