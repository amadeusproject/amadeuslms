from django import forms
from .models import Link
import validators

class CreateLinkForm(forms.ModelForm):
    def validate_link(self,link):
        if not validators.url(link):
            raise forms.ValidationError(_('Please enter a valid URL'))
        else:
            return link

    class Meta:
        model = Link
        fields = ['name','link','description']

class UpdateLinkForm(forms.ModelForm):
    class Meta:
        model = Link
        fields = ['name','link','description']
