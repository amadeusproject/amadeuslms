from django import forms

from users.models import User

class RegisterUserForm(forms.ModelForm):

    password = forms.CharField(label='Senha', widget=forms.PasswordInput)
    password2 = forms.CharField(label = 'Confirmacao de Senha', widget = forms.PasswordInput)
    # birth_date = forms.DateField(widget=forms.SelectDateWidget())
    MIN_LENGTH = 8

    def clean_password(self):
        password = self.cleaned_data.get('password')

        # At least MIN_LENGTH long
        if len(password) < self.MIN_LENGTH:
            raise forms.ValidationError("A senha deve conter  no minimo %d caracteres." % self.MIN_LENGTH)

        # At least one letter and one non-letter
        first_isalpha = password[0].isalpha()
        if all(c.isalpha() == first_isalpha for c in password):
            raise forms.ValidationError("A senha deve conter pelo menos uma letra e pelo menos um digito ou "\
                                        "um caractere de pontuacao.")

        return password

    def clean_password2(self):
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")

        if password and password2 and password != password2:
            raise forms.ValidationError('A confirmmacao de senha esta incorreta')
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