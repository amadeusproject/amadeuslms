from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _


class AmadeusAuthForm(AuthenticationForm):
  username = forms.EmailField(
    widget=forms.EmailInput(
      attrs={
        "class": "form-control",
        "placeholder": _("E-mail"),
      }
    )
  )
  password = forms.CharField(
    widget=forms.PasswordInput(
      attrs={
        "class": "form-control",
        "placeholder": _("Senha"),
      }
    )
  )
