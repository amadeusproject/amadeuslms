from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

from ..defs import EMAIL_VISIBILITY_CHOICES
from ..models import Account


class BaseAccountForm(UserCreationForm):
  class Meta(UserCreationForm.Meta):
    model = Account
    fields = ("email", "firstname", "lastname")

    error_messages = {
      "email": {
        "unique": _("E-mail já cadastrado na plataforma"),
      }
    }


class QuickRegistrationForm(BaseAccountForm):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    for field in self.fields.values():
      field.widget.attrs.update({"class": "form-control", "placeholder": field.label})


class CompleteRegistrationForm(BaseAccountForm):
  socialname = forms.CharField(max_length=255, required=False)
  description = forms.CharField(widget=forms.Textarea, required=False)
  avatar = forms.ImageField(required=False)
  show_email = forms.ChoiceField(choices=EMAIL_VISIBILITY_CHOICES, required=False)

  def save(self, commit=True):
    account = super().save(commit=commit)

    if commit:
      user = account.user

      user.socialname = self.cleaned_data["socialname"]
      user.description = self.cleaned_data["description"]
      user.avatar = self.cleaned_data["avatar"]
      user.show_email = self.cleaned_data["show_email"]
      user.save()

    return account
