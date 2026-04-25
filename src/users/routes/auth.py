from django.contrib.auth import views as password_views
from django.urls import path

from ..views import auth as auth_views

app_name = "auth"
urlpatterns = [
  path("login/", auth_views.AmadeusAuthView.as_view(), name="login"),
  path("logout/", auth_views.AmadeusLogoutView.as_view(), name="logout"),
  path("auth/validate-email/", auth_views.validate_email_view, name="validate_email"),
  path(
    "recuperar-senha/",
    password_views.PasswordResetView.as_view(
      template_name="auth/password_reset.html",
      html_email_template_name="auth/emails/password_reset.html",
      success_url="/recuperar-senha/enviado/",
    ),
    name="password_reset",
  ),
  path(
    "recuperar-senha/enviado/",
    password_views.PasswordResetDoneView.as_view(
      template_name="auth/partials/_password_reset_sent.html",
    ),
    name="password_reset_done",
  ),
  path(
    "recuperar-senha/confirmar/<uidb64>/<token>/",
    password_views.PasswordResetConfirmView.as_view(
      template_name="auth/partials/_password_reset_confirm.html",
    ),
    name="password_reset_confirm",
  ),
  path(
    "recuperar-senha/feito/",
    password_views.PasswordResetCompleteView.as_view(
      template_name="auth/partials/_password_reset_done.html",
    ),
    name="password_reset_complete",
  ),
]
