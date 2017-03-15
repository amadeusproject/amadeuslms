# coding=utf-8
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.html import strip_tags
from django.db.models import Q

from resubmit.widgets import ResubmitFileWidget

from .models import TalkMessages

class Validation(forms.ModelForm):
	MAX_UPLOAD_SIZE = 5*1024*1024

	def clean_text(self):
		text = self.cleaned_data.get('text', '')
		cleaned_text = strip_tags(text)

		if cleaned_text == '':
			self._errors['text'] = [_('This field is required.')]

			return ValueError

		return text

	def clean_image(self):
		image = self.cleaned_data.get('image', False)

		if image:
			if hasattr(image, '_size'):
				if image._size > self.MAX_UPLOAD_SIZE:
					self._errors['image'] = [_("The image is too large. It should have less than 5MB.")]

					return ValueError

		return image

class ChatMessageForm(Validation):
	class Meta:
		model = TalkMessages
		fields = ['text', 'image']
		widgets = {
			'text': forms.Textarea,
			'image': ResubmitFileWidget(attrs={'accept':'image/*'}),
		}