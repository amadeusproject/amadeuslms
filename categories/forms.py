from django import forms
from .models import Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('category_father', 'name', 'description', 'visible', 'coordinators', )
        widgets = {
			'category_father': forms.Select(),
			
		}