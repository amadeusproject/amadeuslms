from django import forms
from .models import Category

from django.utils.translation import ugettext_lazy as _

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ( 'name', 'description', 'visible', 'coordinators', )
        widgets = {
            'description': forms.Textarea,
            'coordinators' : forms.SelectMultiple,
        }
        
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if self.instance.id:
            same_name = Category.objects.filter(name__unaccent__iexact = name).exclude(id = self.instance.id)
        else:
            same_name = Category.objects.filter(name__unaccent__iexact = name)

        if same_name.count() > 0:
            self._errors['name'] = [_('There is another category with this name, try another one.')]

        return name
