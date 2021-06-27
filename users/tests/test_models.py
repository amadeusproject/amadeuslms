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


def test_user_model_default_values():
    pass


def test_user_model_social_name():
    pass


def test_user_model_without_social_name():
    pass


def test_user_get_items():
    pass


def test_user_get_short_name():
    pytest.mark.xfail("not implemented")
