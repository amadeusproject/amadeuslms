from django import forms
from .models import Link
import validators

class CreateLinkForm(forms.ModelForm):

    def clean_link(self):
        link = self.cleaned_data['link']
        if not validators.url(link):
            raise forms.ValidationError(_('Please enter a valid URL'))
        return link

    class Meta:
        model = Link
        fields = ['name','link','description']

class UpdateLinkForm(forms.ModelForm):
    class Meta:
        model = Link
        fields = ['name','link','description']
