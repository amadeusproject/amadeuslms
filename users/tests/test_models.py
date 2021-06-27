from datetime import datetime

import pytest
from django.db.models.fields.files import ImageFieldFile

from users.models import User


@pytest.fixture()
def test_user() -> User:
    return User.objects.create(
        username="test_user",
        last_name="amadeus",
        email="test_user@amadeus.com",
    )


def test_user_model_email_validation():
    pass


@pytest.mark.django_db
def test_user_model_with_valid_fields(test_user):
    assert isinstance(test_user.username, str)
    assert isinstance(test_user.last_name, str)
    assert isinstance(test_user.email, str)
    assert isinstance(test_user.description, str)
    assert isinstance(test_user.date_created, datetime)
    assert isinstance(test_user.last_update, datetime)
    assert isinstance(test_user.is_active, bool)
    assert isinstance(test_user.is_staff, bool)
    assert isinstance(test_user.is_support, bool)
    assert isinstance(test_user.show_email, int)
    assert isinstance(test_user.image, ImageFieldFile)


@pytest.mark.django_db
def test_user_model_social_name(test_user):
    assert test_user.fullname() == test_user.username + " " + test_user.last_name


@pytest.mark.django_db
def test_user_get_items(test_user):
    """
    Testing that when a user is created, there is not logs associated with it.
    """
    assert test_user.get_items().exists() is False


@pytest.mark.django_db
def test_user_get_short_name(test_user):
    assert test_user.get_short_name() == (test_user.social_name or (test_user.username + " " + test_user.last_name))
