# coding=utf-8
import os, re
from datetime import date
from pycpfcnpj import cpfcnpj
from django.conf import settings
from django import forms
from django.utils.translation import ugettext_lazy as _
from rolepermissions.shortcuts import assign_role
from django.contrib.auth.forms import UserCreationForm
from .models import User

class AdminUserForm(forms.ModelForm):
	def save(self, commit=True):
		super(AdminUserForm, self).save(commit=False)

		self.instance.set_password(self.cleaned_data['password'])
		self.instance.save()

		if self.instance.is_staff:
			assign_role(self.instance, 'system_admin')
		elif self.instance.type_profile == 2:
			assign_role(self.instance, 'student')
		elif self.instance.type_profile == 1:
			assign_role(self.instance, 'professor')

		self.instance.save()

		return self.instance

	class Meta:
		model = User
		fields = ['username', 'name', 'email', 'password', 
		'birth_date', 'city', 'state', 'gender', 'type_profile', 'cpf', 'phone', 
		'image', 'titration', 'year_titration', 'institution', 'curriculum', 'is_staff', 'is_active']
		widgets = {
			'password':forms.PasswordInput
		}

class RegisterUserForm(forms.ModelForm):

    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput)
    password2 = forms.CharField(label = _('Confirm Password'), widget = forms.PasswordInput)
    # birth_date = forms.DateField(widget=forms.SelectDateWidget())
    MIN_LENGTH = 8

    def validate_cpf(self, cpf):
        cpf = ''.join(re.findall('\d', str(cpf)))

        if cpfcnpj.validate(cpf):
            return True
        return False

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email = email).exists():
            raise forms.ValidationError(_('There is already a registered User with this e-mail'))
        return email

    def clean_birth_date(self):
        birth_date = self.cleaned_data['birth_date']
        if birth_date >= date.today():
            raise forms.ValidationError(_('Please enter a valid date'))
        return birth_date


    def clean_cpf(self):
        cpf = self.cleaned_data['cpf']
        if (cpf == ""):
            return cpf
        if User.objects.filter(cpf = cpf).exists():
            raise forms.ValidationError(_('There is already a registered User with this CPF'))
        if not self.validate_cpf(cpf):
           raise forms.ValidationError(_('Please enter a valid CPF'))
        return cpf

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
        fields = ['username', 'name', 'email', 'city', 'state', 'gender', 'cpf', 'birth_date', 'phone', 'image', 'titration',
        'year_titration', 'institution', 'curriculum',]

class UserForm(RegisterUserForm):

	class Meta:
		model = User
		fields = ['username', 'name', 'email', 'birth_date', 'city', 
		'state', 'gender', 'type_profile', 'cpf', 'phone', 'image', 'titration', 
		'year_titration', 'institution', 'curriculum', 'is_staff', 'is_active']

class UpdateUserForm(forms.ModelForm):

	def validate_cpf(self, cpf):
		cpf = ''.join(re.findall('\d', str(cpf)))

		if cpfcnpj.validate(cpf):
			return True
		return False

	def clean_cpf(self):
		cpf = self.cleaned_data['cpf']
		if not self.validate_cpf(cpf):
			raise forms.ValidationError(_('Please enter a valid CPF'))
		return cpf

	def clean_birth_date(self):
		birth_date = self.cleaned_data['birth_date']
		if birth_date >= date.today():
			raise forms.ValidationError(_('Please enter a valid date'))
		return birth_date

	class Meta:
		model = User
		fields = ['username', 'name', 'email', 'birth_date', 'city', 
		'state', 'gender', 'type_profile', 'cpf', 'phone', 'image', 'titration', 
		'year_titration', 'institution', 'curriculum', 'is_staff', 'is_active']


		
class UpdateProfileFormAdmin(UpdateUserForm):

	class Meta:
		model = User
		fields = ['username', 'name', 'email', 'birth_date', 'city', 
		'state', 'gender', 'type_profile', 'cpf', 'phone', 'image', 'titration', 
		'year_titration', 'institution', 'curriculum', 'is_staff', 'is_active']

class UpdateProfileForm(UpdateUserForm):

	class Meta:
		model = User
		fields = ['username', 'name', 'email', 'birth_date', 'city', 
		'state', 'gender', 'cpf', 'phone', 'image', 'titration', 
		'year_titration', 'institution', 'curriculum']
