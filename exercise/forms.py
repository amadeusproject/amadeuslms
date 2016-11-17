from .models import Exercise
from django import forms
from django.core.exceptions import ValidationError, FieldError
from django.utils.translation import ugettext_lazy as _
import requests


class ExerciseForm(forms.ModelForm):

    class Meta:
        model = Exercise
        fields = ['name_exercise', 'description', 'init_date',
                    'end_date', 'name_exercise']


class UpdateExerciseForm(forms.ModelForm):

    class Meta:
        model = Exercise
        fields = ['name_exercise', 'description', 'init_date',
                    'end_date', 'grade', 'name_exercise']
