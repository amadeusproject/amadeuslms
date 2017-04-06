from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import News

class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title','image','content']
        widgets = {
            'content': forms.Textarea,
        }
