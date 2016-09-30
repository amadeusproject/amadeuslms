from django import forms
from django.utils.translation import ugettext_lazy as _
from users.models import User
from .models import Poll

class PollForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(PollForm, self).__init__(*args, **kwargs)
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
        model = Poll
        fields = ['name','limit_date','students','all_students']

        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Question?'}),
            'limit_date': forms.DateTimeInput(
                attrs={'placeholder': 'Maximum date permited to resolve the poll'}),
            'student': forms.Select(),
        }
