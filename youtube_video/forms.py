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
from django.forms.models import inlineformset_factory


import requests
import re

from subjects.models import Tag
from subjects.forms import ParticipantsMultipleChoiceField

from pendencies.forms import PendenciesForm
from pendencies.models import Pendencies

from .models import YTVideo


class YTVideoForm(forms.ModelForm):
	subject = None
	control_subject = forms.CharField(widget = forms.HiddenInput())
	students = ParticipantsMultipleChoiceField(queryset = None, required = False)

	def __init__(self, *args, **kwargs):
		super(YTVideoForm, self).__init__(*args, **kwargs)

		self.subject = kwargs['initial'].get('subject', None)

		if self.instance.id:
			self.subject = self.instance.topic.subject
			self.initial['tags'] = ", ".join(self.instance.tags.all().values_list("name", flat = True))

		self.initial['control_subject'] = self.subject.id

		self.fields['students'].queryset = self.subject.students.all()
		self.fields['groups'].queryset = self.subject.group_subject.all()

	tags = forms.CharField(label = _('Tags'), required = False)

	class Meta:
		model = YTVideo
		fields = ['name', 'url', 'brief_description', 'all_students', 'students', 'groups', 'show_window', 'visible']
		labels = {
			'name': _('Video title'),
		}
		widgets = {
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
				self._errors['name'] = [_('This subject already has a resource with this name')]

				return ValueError

		return name

	def clean_url(self):
		url = self.cleaned_data.get('url', '')
		if url[0].lower() != "h": url = "https://" + url
		if  (re.compile("https?://w{3}\.youtube\.com/").match(url) == None
		and re.compile("https?://youtu\.be/").match(url) == None) or requests.get(url).status_code == 404:
			self._errors['url'] = [_('Invalid URL. It should be an YouTube link.')]
			return ValueError
		if re.compile("https?://youtu\.be/").match(url) != None:
			url = url.replace("youtu.be","www.youtube.com/embed")
		return url

	def save(self, commit = True):
		super(YTVideoForm, self).save(commit = True)

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

InlinePendenciesFormset = inlineformset_factory(YTVideo, Pendencies, form = PendenciesForm, extra = 1, max_num = 3, validate_max = True, can_delete = True)
