from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import Forum

class ForumForm(forms.ModelForm):

	class Meta:
		model = Forum
		fields = ('title', 'description')
		labels = {
			'title': _('Title'),
			'description': _('Description')
		}
		help_texts = {
			'title': _('Forum title'),
			'description': _('What is this forum about?')
		}
		widgets = {
			'description': forms.Textarea(attrs={'cols': 80, 'rows': 5}),
		}