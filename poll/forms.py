from django import forms
from django.utils.translation import ugettext_lazy as _
from users.models import User
from .models import Poll

class PollForm(forms.ModelForm):

    # password = forms.CharField(label=_('Password'), widget=forms.PasswordInput)
    # password2 = forms.CharField(label = _('Password confirmation'), widget = forms.PasswordInput)
    # birth_date = forms.DateField(widget=forms.SelectDateWidget())
    # MIN_LENGTH = 8

    class Meta:
        model = Poll
        # exclude = ['is_staff', 'is_active']
        fields = ['name','limit_date']

        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Question?'}),
            'description': forms.DateTimeInput(
                attrs={'placeholder': 'Maximum date permited to resolve the poll'}),
        }
