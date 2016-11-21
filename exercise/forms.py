from .models import Exercise
from django import forms
from django.core.exceptions import ValidationError, FieldError
from django.utils.translation import ugettext_lazy as _
import requests


class ExerciseForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ExerciseForm, self).__init__(*args, **kwargs)
        self.fields["allowed"].required = False
        self.fields["allowed"].initial = False

    # def clean_allowed(self):
    #     if('allowed' in self.data):
    #         allowed = self.data['allowed']
    #         raise forms.ValidationError(_('It is required one these fields.'))
    #     return True

    class Meta:
        model = Exercise
        fields = ['name_exercise', 'description',
                    'end_date', 'file', 'allowed']


class UpdateExerciseForm(forms.ModelForm):

    class Meta:
        model = Exercise
        fields = ['name_exercise', 'description',
                    'end_date', 'file']
