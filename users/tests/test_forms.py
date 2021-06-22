import pytest

from users.forms import RegisterUserForm


@pytest.mark.django_db
@pytest.mark.parametrize(
    'email, username, password2, last_name, social_name, image, show_email, x, y, width, height, new_password, validity',
    [(None, None, None, None, None, None, None, None, None, None, None, None, False),
     ('test@amadeus.com', 'test', 'pass_test', "test_last_name", "test_social", None, None, None, None, None, None,
      'pass_test', True),
     ('test@amadeus.com', 'test', 'pass_test', "test_last_name", "test_social", None, 1, None, None, None, None,
      'pass_test', True),
     ('test@amadeus.com', 'test', 'pass_test', "test_last_name", "test_social", None, 2, None, None, None, None,
      'pass_test', True),
     ('test@amadeus.com', 'test', 'pass_test', "test_last_name", "test_social", None, 3, None, None, None, None,
      'pass_test', True)
     ]
)
def test_register_user_form(email, username, password2, last_name, social_name, image, show_email, x, y, width, height,
                            new_password, validity):
    form = RegisterUserForm(data={'email': email, 'username': username, 'password2': password2, 'last_name': last_name,
                                  'social_name': social_name, 'image': image, 'show_email': show_email, 'x': x,
                                  'y': y, 'width': width, 'height': height, 'new_password': new_password})
    print(form.errors)
    assert form.is_valid() is validity


def test_register_user_form_fields():
    """
    GIVEN  the form RegisterUserForm
    WHEN the form RegisterUserForm is created
    THEN it must have the following fields on it.
    """
    form = RegisterUserForm()
    assert list(form.fields) == ["email", "username", "last_name", "social_name", "image", "show_email", "x", "y",
                                 "width",
                                 "height",
                                 "new_password", "password2"]
