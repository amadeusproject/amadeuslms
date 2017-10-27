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