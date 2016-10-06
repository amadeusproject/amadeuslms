# coding=utf-8
import os, re
from datetime import date
from pycpfcnpj import cpfcnpj
from django.conf import settings
from django import forms
from django.utils.translation import ugettext_lazy as _
from rolepermissions.shortcuts import assign_role
from django.contrib.auth.forms import UserCreationForm
from core.forms import RegisterUserForm
from .models import User

class UserForm(RegisterUserForm):

	class Meta:
		model = User
		fields = ['username', 'name', 'email', 'birth_date', 'city', 'state', 'gender', 'type_profile', 'cpf', 'phone', 'image', 'is_staff', 'is_active']

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
		fields = ['username', 'name', 'email', 'city', 'state', 'birth_date', 'gender', 'type_profile', 'cpf', 'phone', 'image', 'is_staff', 'is_active']

class UpdateProfileForm(UpdateUserForm):

	class Meta:
		model = User
		fields = ['username', 'name', 'email', 'birth_date', 'city', 'state', 'gender', 'cpf', 'phone', 'image']
