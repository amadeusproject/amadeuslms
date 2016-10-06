from django import forms
from .models import Link

class CreateLinkForm(forms.ModelForm):
    class Meta:
        model = Link
        fields = ['name','link','description']
        
class UpdateLinkForm(forms.ModelForm):
    class Meta:
        model = Link
        fields = ['name','link','description']
