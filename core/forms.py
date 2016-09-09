from django import forms
from django.utils.translation import ugettext_lazy as _
from users.models import User

class RegisterUserForm(forms.ModelForm):

    password = forms.CharField(label='Senha', widget=forms.PasswordInput)
    password2 = forms.CharField(label = 'Confirmacao de Senha', widget = forms.PasswordInput)
    # birth_date = forms.DateField(widget=forms.SelectDateWidget())
    MIN_LENGTH = 8

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email = email).exists():
            raise forms.ValidationError(_('There is already a registered User with this e- mail'))
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')

        # At least MIN_LENGTH long
        if len(password) < self.MIN_LENGTH:
            raise forms.ValidationError(_("The password must contain at least % d characters." % self.MIN_LENGTH))

        # At least one letter and one non-letter
        first_isalpha = password[0].isalpha()
        if all(c.isalpha() == first_isalpha for c in password):
            raise forms.ValidationError(_('The password must contain at least one letter and at least one digit or '\
                                        "a punctuation character."))

        return password

    def clean_password2(self):
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")

        if password and password2 and password != password2:
            raise forms.ValidationError(_('The confirmation password is incorrect.'))
        return password2

    def save(self, commit=True):
        super(RegisterUserForm, self).save(commit=False)
        self.instance.set_password(self.cleaned_data['password'])
        
        self.instance.save()
        return self.instance

    class Meta:
        model = User
        # exclude = ['is_staff', 'is_active']
        fields = ['username', 'name', 'email', 'city', 'state', 'gender', 'cpf', 'birth_date', 'phone', 'image']