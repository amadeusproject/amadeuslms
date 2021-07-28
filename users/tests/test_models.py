"""
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco

Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS

O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.

Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.

Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

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
