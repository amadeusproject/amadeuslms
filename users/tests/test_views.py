import pytest
from django.test.client import Client
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from pytest_django.asserts import assertTemplateUsed

from users.models import User
from users.views import Profile


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
def test_delete_view(login_user, test_student):
    client = login_user
    response = client.get(reverse('users:delete', kwargs={'email': test_student.email}))
    assert response.status_code == 200
    assertTemplateUsed(response, "users/delete.html")

    # Logs are created that a user has been deleted


@pytest.mark.django_db
def test_create_view(login_user):
    client = login_user
    response = client.get(reverse('users:create'))
    assert response.status_code == 200
    assertTemplateUsed(response, "users/create.html")
    assertTemplateUsed(response, "users/_form.html")


@pytest.mark.django_db
def test_signup_view():
    pass


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
def test_reset_password_view(login_user):
    client = login_user


@pytest.mark.django_db
def test_search_view():
    # requires admin user
    pass


@pytest.mark.django_db
def test_support_view():
    # requires admin user
    pass
