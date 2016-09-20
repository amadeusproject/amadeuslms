# coding=utf-8
import os
from django.conf import settings
from django import forms
from django.utils.translation import ugettext_lazy as _
from rolepermissions.shortcuts import assign_role
from .models import User


class ProfileForm(forms.ModelForm):

	def save(self, commit=True):
		super(ProfileForm, self).save(commit=False)

		self.instance.set_password(self.cleaned_data['password'])
		self.instance.save()

		return self.instance

	class Meta:
		model = User
		fields = ['username', 'name', 'email', 'password', 'birth_date', 'city', 'state', 'gender', 'cpf', 'phone', 'image']
		widgets = {
			'password':forms.PasswordInput
		}	

class UserForm(forms.ModelForm):
	def save(self, commit=True):
		super(UserForm, self).save(commit=False)

		#if not self.instance.image:
		#	self.instance.image = os.path.join(os.path.dirname(settings.BASE_DIR), 'uploads', 'no_image.jpg')

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
		fields = ['username', 'name', 'email', 'password', 'birth_date', 'city', 'state', 'gender', 'type_profile', 'cpf', 'phone', 'image', 'is_staff', 'is_active']
		widgets = {
			'password':forms.PasswordInput
		}

class EditUserForm(forms.ModelForm):

	class Meta:
		model = User
		fields = ['username', 'name', 'email', 'birth_date', 'city', 'state', 'gender', 'cpf', 'phone', 'image']

# Ailson
class UpdateUserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['username', 'name', 'email', 'city', 'state', 'birth_date', 'gender', 'cpf', 'phone', 'image']
