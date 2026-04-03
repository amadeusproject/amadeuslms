from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView

from ..forms.account import QuickRegistrationForm


class AutoRegistrationView(CreateView):
  form_class = QuickRegistrationForm
  template_name = "account/signup.html"
  success_url = reverse_lazy("auth:login")

  def get_template_names(self):
    if self.request.htmx:
      return ["account/partials/_form_signup.html"]
    return [self.template_name]

  def form_valid(self, form):
    user = form.save(commit=False)
    user.is_active = False
    user.save()

    current_site = get_current_site(self.request)
    subject = _("Confirme seu cadastro")
    message = render_to_string(
      "account/emails/activation_email.html",
      {
        "user": user,
        "domain": current_site.domain,
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": default_token_generator.make_token(user),
      },
    )

    user.email_user(subject, message)

    messages.success(
      self.request,
      _(
        "Cadastro realizado com sucesso! Verifique seu e-mail para confirmar a conta antes de fazer login."
      ),
    )

    if self.request.htmx:
      response = HttpResponse()
      response["HX-Redirect"] = self.success_url
      return response

    return super().form_valid(form)

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context["title"] = _("Criar conta")
    return context


def validate_email_view(request):
  email = request.POST.get("email")

  form = QuickRegistrationForm(data={"email": email})

  form.full_clean()
  errors = form.errors.get("email", [])

  if errors:
    return HttpResponse(errors[0])

  return HttpResponse("")


def activate(request, uidb64, token):
  User = get_user_model()
  try:
    uid = urlsafe_base64_decode(uidb64)
    user = User.objects.get(pk=uid)
  except (TypeError, ValueError, OverflowError, User.DoesNotExist):
    user = None

  if user is not None and default_token_generator.check_token(user, token):
    user.is_active = True
    user.save()
    messages.success(request, _("Conta ativada com sucesso!"))
    return redirect("auth:login")
  else:
    messages.error(request, _("Link de ativação inválido ou expirado."))
    return redirect("auth:login")
