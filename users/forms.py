# coding=utf-8
from django import forms
from django.utils.translation import ugettext_lazy as _
from rolepermissions.shortcuts import assign_role
from django.contrib.auth import update_session_auth_hash
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import User

class Validation(forms.ModelForm):
	MIN_PASS_LENGTH = 8
	MAX_UPLOAD_SIZE = 2*1024*1024

	def clean_email(self):
		email = self.cleaned_data.get('email', '')

		try:
			validate_email( email )
			return email
		except ValidationError:
			self._errors['email'] = [_('You must insert an email address')]
			
			return ValueError

	def clean_image(self):
		image = self.cleaned_data.get('image', False)

		if image:
			if hasattr(image, '_size'):
				if image._size > self.MAX_UPLOAD_SIZE:
					self._errors['image'] = [_("The image is too large. It should have less than 2MB.")]

					return ValueError

		return image

	# def clean_new_password(self):
	# 	password = self.cleaned_data.get('new_password')

	# 	if self.is_edit and len(password) == 0:
	# 		return password

 #        # At least MIN_LENGTH long
	# 	if len(password) < self.MIN_PASS_LENGTH:
	# 		self._errors['new_password'] = [_("The new password must contain at least % d characters." % self.MIN_PASS_LENGTH)]
			
	# 		return ValueError

 #        # At least one letter and one non-letter
	# 	first_isalpha = password[0].isalpha()
	# 	if all(c.isalpha() == first_isalpha for c in password):
	# 		self._errors['new_password'] = [_('The password must contain at least one letter and at least one digit or a punctuation character.')]

	# 		return ValueError

	# 	return password

	def clean_password2(self):
		password = self.cleaned_data.get("new_password")
		password2 = self.cleaned_data.get("password2")

		#if self.is_edit and len(password) == 0:
		#	return password2

		if password and password2 and password != password2:
			self._errors['password2'] = [_('The confirmation password is incorrect.')]

			return ValueError
        
		return password2	

class RegisterUserForm(Validation):
    new_password = forms.CharField(label=_('Password'), widget = forms.PasswordInput(render_value=True))
    password2 = forms.CharField(label = _('Confirm Password'), widget = forms.PasswordInput(render_value=True))

    is_edit = False

    def save(self, commit=True):
        super(RegisterUserForm, self).save(commit=False)
        
        self.instance.set_password(self.cleaned_data['new_password'])

        self.instance.save()
        
        return self.instance

    class Meta:
        model = User
        fields = ['email', 'username', 'last_name', 'social_name', 'image', 'show_email', ]

class ProfileForm(Validation):
	is_edit = True

	def save(self, commit=True):
		super(ProfileForm, self).save(commit=False)
        
		self.instance.save()
        
		return self.instance

	class Meta:
		model = User
		fields = ['email', 'username', 'last_name', 'social_name', 'description', 'show_email', 'image']
		widgets = {
			'description': forms.Textarea,
			'username': forms.TextInput(attrs = {'readonly': 'readonly'}),
			'last_name': forms.TextInput(attrs = {'readonly': 'readonly'})
		}

class UserForm(Validation):
	is_edit = False

	def __init__(self, *args, **kwargs):
		is_update = kwargs.pop('is_edit', False)

		super(UserForm, self).__init__(*args, **kwargs)

		self.is_edit = is_update

		if self.is_edit:
			del self.fields['new_password']
			del self.fields['password2']
		    
	if not is_edit:
		new_password = forms.CharField(label=_('Password'), widget = forms.PasswordInput(render_value=True), required = False)
		password2 = forms.CharField(label = _('Confirm Password'), widget = forms.PasswordInput(render_value=True), required = False)


	def save(self, commit=True):
		super(UserForm, self).save(commit=False)
        
		if not self.is_edit:
			self.instance.set_password(self.cleaned_data['new_password'])

		self.instance.save()
        
		return self.instance

	class Meta:
		model = User
		fields = ['email', 'username', 'last_name', 'social_name', 'description', 'show_email', 'image', 'is_staff', 'is_active']
		widgets = {
			'description': forms.Textarea,
		}

class ChangePassForm(Validation):
	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user', None)
		self.request = kwargs.pop('request', None)
		super(ChangePassForm, self).__init__(*args, **kwargs)

	is_edit = False

	new_password = forms.CharField(label=_('New Password'), widget = forms.PasswordInput(render_value=True), required = True)
	password2 = forms.CharField(label = _('Confirm Password'), widget = forms.PasswordInput(render_value=True), required = True)

	def clean_password(self):
		password = self.cleaned_data.get('password', None)

		if not self.user.check_password(password):
			self._errors['password'] = [_('The value inputed does not match with your actual password.')]

			return ValueError

		return password

	def save(self, commit=True):
		super(ChangePassForm, self).save(commit=False)
        
		self.instance.set_password(self.cleaned_data['new_password'])

		update_session_auth_hash(self.request, self.instance)

		self.instance.save()
        
		return self.instance

	class Meta:
		model = User
		fields = ['password']
		labels = {
			'password': _('Actual Password')
		}
		widgets = {
			'password': forms.PasswordInput
		}

class PassResetRequest(forms.Form):
	email = forms.CharField(label = _('Email'), max_length = 254)

	def clean_email(self):
		email = self.cleaned_data.get('email', '')

		try:
			validate_email( email )
			return email
		except ValidationError:
			self._errors['email'] = [_('You must insert an email address')]
			
			return ValueError

class SetPasswordForm(Validation):
	is_edit = False

	new_password = forms.CharField(label=_('New Password'), widget = forms.PasswordInput(render_value=True), required = True)
	password2 = forms.CharField(label = _('Confirm Password'), widget = forms.PasswordInput(render_value=True), required = True)

	class Meta:
		model = User
		fields = []