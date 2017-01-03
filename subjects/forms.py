from .models import Subject, Marker
from django import forms
class CreateSubjectForm(forms.ModelForm):
    # TODO: Define form fields here
    class Meta:
        model = Subject

        fields = ('name', 'description_brief', 'description', 'markers', 'init_date', 'end_date', 'visible', 'professor',
        'students', )

        widgets = {
            'description_brief': forms.Textarea,
            'description': forms.Textarea,
            'professor': forms.SelectMultiple,
            'students': forms.SelectMultiple,
        }



class CreateMarkerForm(forms.ModelForm):
    class Meta:
        model = Marker
        fields = ('name',)
    