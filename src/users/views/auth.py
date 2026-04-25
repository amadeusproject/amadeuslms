from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _

from logger.service import entry_log
from users.forms.auth import AmadeusAuthForm


class AmadeusAuthView(LoginView):
  form_class = AmadeusAuthForm
  template_name = "auth/login.html"
  partial_template_name = "auth/partials/_form_login.html"

  def get_template_names(self):
    if self.request.htmx:
      return [self.partial_template_name]
    return [self.template_name]

  def form_valid(self, form):
    auth_login(self.request, form.get_user())

    entry_log(self.request.user, "login", None, {})

    if self.request.htmx:
      response = HttpResponse()
      response["HX-Redirect"] = self.get_success_url()
      return response

    return super().form_valid(form)

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context["title"] = _("Entrar")
    return context


class AmadeusLogoutView(LogoutView):
  next_page = "auth:login"

  def dispatch(self, request, *args, **kwargs):
    entry_log(request.user, "logout", None, {})

    messages.info(request, _("Você saiu da sua conta."))

    return super().dispatch(request, *args, **kwargs)


def validate_email_view(request):
  email = request.POST.get("username")

  form = AmadeusAuthForm(data={"username": email})

  form.full_clean()
  errors = form.errors.get("username", [])

  if errors:
    return HttpResponse(errors[0])

  return HttpResponse("")
