""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

# coding=utf-8
from django import forms
from django.utils.translation import ugettext_lazy as _, pgettext_lazy
from django.utils.html import strip_tags
from django.db.models import Q

from resubmit.widgets import ResubmitFileWidget

from topics.models import Resource

from .models import GeneralPost, CategoryPost, SubjectPost, Comment

class Validation(forms.ModelForm):
	MAX_UPLOAD_SIZE = 5*1024*1024

	def __init__(self, *args, **kwargs):
		super(Validation, self).__init__(*args, **kwargs)
		CHOICES = (("comment", pgettext_lazy("form","Comment")), ("help", pgettext_lazy("form","Ask for Help")))
		self.fields['action'].choices = CHOICES

	def clean_post(self):
		post = self.cleaned_data.get('post', '')
		cleaned_post = strip_tags(post)

		if cleaned_post == '':
			self._errors['post'] = [_('This field is required.')]

			return ValueError

		return post

	def clean_image(self):
		image = self.cleaned_data.get('image', False)

		if image:
			if hasattr(image, '_size'):
				if image._size > self.MAX_UPLOAD_SIZE:
					self._errors['image'] = [_("The image is too large. It should have less than 5MB.")]

					return ValueError

		return image


class GeneralPostForm(Validation):

	class Meta:
		model = GeneralPost
		fields = ['action', 'post', 'image']

		widgets = {
			'action': forms.RadioSelect,
			'post': forms.Textarea,
			'image': ResubmitFileWidget(attrs={'accept':'image/*'}),
		}

class CategoryPostForm(Validation):
	class Meta:
		model = CategoryPost
		fields = ['action', 'post', 'image']
		widgets = {
			'action': forms.RadioSelect,
			'post': forms.Textarea,
			'image': ResubmitFileWidget(attrs={'accept':'image/*'}),
		}

class SubjectPostForm(Validation):
	def __init__(self, *args, **kwargs):
		super(SubjectPostForm, self).__init__(*args, **kwargs)

		user = kwargs['initial'].get('user', None)
		subject = kwargs['initial'].get('subject', None)

		if not kwargs['instance'] is None:
			subject = self.instance.space

		if user.is_staff:
			self.fields['resource'].choices = [(r.id, str(r)) for r in Resource.objects.filter(Q(topic__subject = subject))]
		else:
			self.fields['resource'].choices = [(r.id, str(r)) for r in Resource.objects.filter(Q(topic__subject = subject) & (Q(all_students = True) | Q(students = user) | Q(groups__participants = user)))]

		self.fields['resource'].choices.append(("", _("Choose an especific resource")))

	class Meta:
		model = SubjectPost
		fields = ['action', 'resource', 'post', 'image']
		widgets = {
			'action': forms.RadioSelect,
			'post': forms.Textarea,
			'image': ResubmitFileWidget(attrs={'accept':'image/*'}),
		}

class ResourcePostForm(Validation):
	class Meta:
		model = SubjectPost
		fields = ['action', 'post', 'image']
		widgets = {
			'action': forms.RadioSelect,
			'post': forms.Textarea,
			'image': ResubmitFileWidget(attrs={'accept':'image/*'}),
		}

class CommentForm(forms.ModelForm):
	MAX_UPLOAD_SIZE = 5*1024*1024

	def clean_comment(self):
		comment = self.cleaned_data.get('comment', '')
		cleaned_comment = strip_tags(comment)

		if cleaned_comment == '':
			self._errors['comment'] = [_('This field is required.')]

			return ValueError

		return comment

	def clean_image(self):
		image = self.cleaned_data.get('image', False)

		if image:
			if hasattr(image, '_size'):
				if image._size > self.MAX_UPLOAD_SIZE:
					self._errors['image'] = [_("The image is too large. It should have less than 5MB.")]

					return ValueError

		return image

	class Meta:
		model = Comment
		fields = ['comment', 'image']
		widgets = {
			'image': ResubmitFileWidget(attrs={'accept':'image/*'}),
		}
