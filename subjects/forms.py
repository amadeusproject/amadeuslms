from .models import Subject, Marker
from django import forms
class CreateSubjectForm(forms.ModelForm):
    # TODO: Define form fields here
    model = Subject

    fields = ('name', 'description_brief', 'description', 'init_date', 'end_date', 'visible', 'markers', 'professor',
	'students', 'category', )


class CreateMarkerForm(forms.ModelForm):
    class Meta:
        model = Marker
        fields = ('name',)
    