""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

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