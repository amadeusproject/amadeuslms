# coding=utf-8
from django import forms
from django.utils.translation import ugettext_lazy as _
from rolepermissions.shortcuts import assign_role
from .models import User

class Validation(forms.ModelForm):
	def clean_password(self):
		password = self.cleaned_data.get('password')

		if self.is_edit and len(password) == 0:
			return password

        # At least MIN_LENGTH long
		if len(password) < self.MIN_LENGTH:
			raise forms.ValidationError(_("The password must contain at least % d characters." % self.MIN_LENGTH))

        # At least one letter and one non-letter
		first_isalpha = password[0].isalpha()
		if all(c.isalpha() == first_isalpha for c in password):
			raise forms.ValidationError(_('The password must contain at least one letter and at least one digit or a punctuation character.'))

		return password

	def clean_password2(self):
		password = self.cleaned_data.get("password")
		password2 = self.cleaned_data.get("password2")

		if self.is_edit and len(password) == 0:
			return password2

		if password and password2 and password != password2:
			raise forms.ValidationError(_('The confirmation password is incorrect.'))
        
		return password2	

class RegisterUserForm(Validation):
    password = forms.CharField(label=_('Password'), widget = forms.PasswordInput)
    password2 = forms.CharField(label = _('Confirm Password'), widget = forms.PasswordInput)

    MIN_LENGTH = 8
    is_edit = False

    def save(self, commit=True):
        super(RegisterUserForm, self).save(commit=False)
        
        self.instance.set_password(self.cleaned_data['password'])

        self.instance.save()
        
        return self.instance

    class Meta:
        model = User
        fields = ['email', 'username', 'last_name', 'social_name',]

class ProfileForm(Validation):
	password = forms.CharField(label=_('Password'), widget = forms.PasswordInput, required = False)
	password2 = forms.CharField(label = _('Confirm Password'), widget = forms.PasswordInput, required = False)

	MIN_LENGTH = 8
	is_edit = True

	def save(self, commit=True):
		super(ProfileForm, self).save(commit=False)
        
		if len(self.cleaned_data['password']) > 0:
			self.instance.set_password(self.cleaned_data['password'])

		self.instance.save()
        
		return self.instance

	class Meta:
		model = User
		fields = ['social_name', 'description', 'show_email', 'image']
		widgets = {
			'description': forms.Textarea,
		}