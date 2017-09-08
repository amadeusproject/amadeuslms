# coding=utf-8
from django import forms
from django.utils.translation import ugettext_lazy as _

from subjects.models import Subject
from subjects.forms import ParticipantsMultipleChoiceField

from .models import StudentsGroup

class StudentsGroupForm(forms.ModelForm):
	subject = None
	participants = ParticipantsMultipleChoiceField(queryset = None, required = False)

	def __init__(self, *args, **kwargs):
		super(StudentsGroupForm, self).__init__(*args, **kwargs)

		self.subject = kwargs['initial'].get('subject', None)
		
		if self.instance.id:
			self.subject = self.instance.subject

		self.fields['participants'].queryset = self.subject.students.all()

	def clean_name(self):
		name = self.cleaned_data.get('name', '')
		
		if self.instance.id:
			same_name = self.subject.group_subject.filter(name__unaccent__iexact = name).exclude(id = self.instance.id).count()
		else:
			same_name = self.subject.group_subject.filter(name__unaccent__iexact = name).count()
		
		if same_name > 0:
			self._errors['name'] = [_('This subject already has a group with this name')]

			return ValueError

		return name

	class Meta:
		model = StudentsGroup
		fields = ['name', 'description', 'participants']
		widgets = {
			'description': forms.Textarea,
			'participants': forms.SelectMultiple,
		}