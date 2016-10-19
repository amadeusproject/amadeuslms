from django import forms
from django.utils.translation import ugettext_lazy as _
from users.models import User
from .models import Exam

class ExamForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ExamForm, self).__init__(*args, **kwargs)
        self.fields["all_students"].required = False
        self.fields["all_students"].initial = False
        self.fields["students"].required = False

    def clean_all_students(self):
        if('all_students' not in self.data):
            if('students' in self.data):
                return False
            raise forms.ValidationError(_('It is required one these fields.'))
        else:
            all_students = self.data['all_students']
            if(not all_students):
                raise forms.ValidationError(_('It is required one these fields.'))
        return True


    class Meta:
        model = Exam
        fields = ['name','begin_date','limit_date','students','all_students']

        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Exam?'}),
			'begin_date': forms.DateTimeInput(
				attrs={'placeholder': _('Start date to resolve the exam')}),
            'limit_date': forms.DateTimeInput(
                attrs={'placeholder': _('Maximum date permited to resolve the exam')}),
            'student': forms.Select(),
        }
