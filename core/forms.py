from django import forms

from users.models import User

class CreateUserForm(forms.ModelForm):

    password = forms.CharField(label='Senha', widget=forms.PasswordInput)

    def save(self, commit=True):
        super(CreateUserForm, self).save(commit=False)
        self.instance.set_password(self.cleaned_data['password'])
        
        self.instance.save()
        return self.instance

    class Meta:
        model = User
        # exclude = ['is_staff', 'is_active']
        fields = ['username', 'name', 'email', 'city', 'state', 'birth_date', 'gender', 'cpf', 'phone', 'image']