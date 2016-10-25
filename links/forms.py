from django import forms
from .models import Link
import validators

class CreateLinkForm(forms.ModelForm):

    def clean_link(self):
        link_url = self.cleaned_data['link_url']
        if not validators.url(link_url):
            raise forms.ValidationError(_('Please enter a valid URL'))
        return link_url

    class Meta:
        model = Link
        fields = ['name','link_url','link_description']

class UpdateLinkForm(forms.ModelForm):
    class Meta:
        model = Link
        fields = ['name','link_url','link_description']
