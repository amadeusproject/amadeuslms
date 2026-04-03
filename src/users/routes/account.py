from django.urls import path

from ..views import account as account_views

app_name = "account"
urlpatterns = [
  path("cadastrar/", account_views.AutoRegistrationView.as_view(), name="signup"),
  path(
    "account/validate-email/", account_views.validate_email_view, name="validate_email"
  ),
  path("ativar/<uidb64>/<token>/", account_views.activate, name="activate"),
]
