"""
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco

Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS

O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.

Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.

Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

import pytest

from users.forms import RegisterUserForm, ProfileForm


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
    if validity:
        user = form.save()
        # I don't compare passwords because we don't have access to the hash function from here
        assert user.email == email
        assert user.username == username
        assert user.last_name == last_name
        assert user.social_name == social_name
        assert user.show_email == show_email


@pytest.mark.django_db
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


@pytest.mark.django_db
def test_profile_form_fields():
    form = ProfileForm()
    assert set(list(form.fields)) == set(["email",
                                          "username",
                                          "last_name",
                                          "social_name",
                                          "description",
                                          "show_email",
                                          "image", "x", "y", "height", "width"])