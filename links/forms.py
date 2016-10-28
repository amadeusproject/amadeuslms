from django import forms
from .models import Link
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError, FieldError
import requests

class CreateLinkForm(forms.ModelForm):

    def clean_link_url(self):
        link_url = self.cleaned_data['link_url']
        try:
            response = requests.head(link_url)
            if response.status_code >= 400:
                raise forms.ValidationError(_('Invalid url!'))
        except requests.ConnectionError:
            raise forms.ValidationError(_('Invalid url!'))
        return link_url

    class Meta:
        model = Link
        fields = ['name','link_url','link_description']

class UpdateLinkForm(forms.ModelForm):
    class Meta:
        model = Link
        fields = ['name','link_url','link_description']
