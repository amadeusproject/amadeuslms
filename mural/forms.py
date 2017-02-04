# coding=utf-8
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.html import strip_tags

from .models import GeneralPost

class Validation(forms.ModelForm):
	MAX_UPLOAD_SIZE = 5*1024*1024

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
			'post': forms.Textarea
		}