"""
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco

Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS

O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.

Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.

Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

import pytest
from django.test.client import Client
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from pytest_django.asserts import assertTemplateUsed

from users.forms import RegisterUserForm
from users.models import User
from users.views import Profile, RegisterUser


@pytest.mark.django_db
@pytest.fixture()
def login_user(test_student):
    client = Client()
    client.force_login(test_student)
    return client


@pytest.fixture()
@pytest.mark.django_db
def test_student():
    test_user = User.objects.create(email="test@amadeus.com", password="random_password")
    test_user.save()
    return test_user


@pytest.fixture()
@pytest.mark.django_db
def admin_user():
    admin_user = User.objects.create(email="test_admin@amadeus.com", password="random_password", is_staff=True)
    admin_user.save()
    return admin_user


@pytest.mark.django_db
def test_user_login_get():
    """
    GIVEN there is no user logged in in
    WHEN the user  opens the login URL
    THEN a web page is returned with status 200 and uses the template users/login.html
    """
    client = Client()
    response = client.get(reverse("users:login"))

    assert response.status_code == 200
    assertTemplateUsed(response, "users/login.html")


@pytest.mark.django_db
def test_delete_view_redirect_without_admin_user(login_user):
    client = login_user
    response = client.get(reverse('users:delete'), kwargs={"email": "test@amadeus.com"})
    assert response.status_code == 302


@pytest.mark.django_db
def test_delete_view_log_creation(admin_user, test_student):
    client = Client()
    client.force_login(admin_user)
    response = client.get(reverse('users:delete', kwargs={"email": test_student.email}))
    assert response.status_code == 200

    deleted_user = User.objects.get(email=test_student.email)
    assert deleted_user is True


@pytest.mark.django_db
def test_delete_view_valid_form_submission(login_user, test_student):
    pass


@pytest.mark.django_db
def test_create_view_redirect_when_logged_user_is_not_admin(login_user):
    client = login_user
    response = client.get(reverse('users:create'), follow=True)
    assert "login" in response.redirect_chain[0][0]
    assert 302 == response.redirect_chain[0][1]


@pytest.mark.django_db
def test_create_view_response_when_user_is_admin(admin_user):
    client = Client()
    client.force_login(admin_user)

    response = client.get(reverse('users:create'))
    assert response.status_code == 200
    assertTemplateUsed(response, "users/create.html")
    assertTemplateUsed(response, "users/_form.html")


@pytest.mark.django_db
def test_signup_view_default_values():
    view = RegisterUser()
    assert view.success_url == reverse_lazy("users:login")
    assert view.form_class == RegisterUserForm
    assert view.template_name == "users/register.html"
    assert view.model == User


@pytest.mark.django_db
def test_signup_view_context_data(login_user):
    client = login_user

    response = client.get(reverse('users:signup'))
    assert response.status_code == 200
    assert isinstance(response.context_data, dict)
    assert response.context_data['title'] == _("Sign Up")


@pytest.mark.django_db
def test_signup_view_form_is_valid():
    client = Client()
    response = client.post("users/signup/", {"email": "teste"})
    assert response.status_code == 200


@pytest.mark.django_db
def test_profile_view(login_user, test_student):
    # test without a logged in user
    # it should redirect to the login page
    anonymous_client = Client()
    response = anonymous_client.get(reverse('users:profile'))
    assert response.status_code == 302

    # test if it redirects to the correct page
    response = anonymous_client.get(reverse('users:profile'), follow=True)
    assert response.status_code == 200
    assert response.redirect_chain[0][1] == 302
    assert "login" in response.redirect_chain[0][0]

    # test with a logged in user
    client = login_user
    response = client.get(reverse('users:profile'))
    assert response.status_code == 200
    assertTemplateUsed(response, "users/profile.html")

    view = Profile()
    view.object = test_student
    # Test if there is a title in the context_data which is our custom code
    assert "title" in view.get_context_data().keys()
    # if there is a title, it should have the following value
    assert view.get_context_data()["title"] == _("Profile")


@pytest.mark.django_db
def test_reset_password_view_without_login():
    # test without a logged in user
    # it should redirect to the login page
    anonymous_client = Client()
    response = anonymous_client.get(reverse('users:forgot_pass'))
    assert response.status_code == 200
    assertTemplateUsed(response, "users/forgot_password.html")


@pytest.mark.django_db
def test_reset_password_view_invalid_email(login_user):
    client = Client()
    response = client.post(reverse('users:forgot_pass'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_search_view():
    # requires admin user
    pass


@pytest.mark.django_db
def test_support_view():
    # requires admin user
    pass
