from django import forms
from .models import Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ( 'name', 'description', 'visible', 'coordinators', )
        widgets = {
			'description': forms.Textarea,
			'coordinators' : forms.SelectMultiple,
		}
       