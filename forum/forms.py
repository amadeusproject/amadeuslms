from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import Forum, Post, PostAnswer

class ForumForm(forms.ModelForm):

	class Meta:
		model = Forum
		fields = ('name', 'description')
		labels = {
			'name': _('Title'),
			'description': _('Description')
		}
		help_texts = {
			'name': _('Forum title'),
			'description': _('What is this forum about?')
		}
		widgets = {
			'description': forms.Textarea(attrs={'cols': 80, 'rows': 5}),
		}

class PostForm(forms.ModelForm):
	
	class Meta:
		model = Post
		fields = ('message', 'forum', )
		labels = {
			'message': _('Message')
		}
		widgets = {
			'message': forms.Textarea(attrs={'cols': 80, 'rows': 3}),
			'forum': forms.HiddenInput(),
		}

class PostAnswerForm(forms.ModelForm):

	class Meta:
		model = PostAnswer
		fields = ('message', )
		labels = {
			'message': _('Message')
		}
		widgets = {
			'message': forms.Textarea(attrs={'cols': 80, 'rows': 3}),
		}