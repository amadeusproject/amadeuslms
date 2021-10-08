"""
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco

Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS

O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.

Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.

Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

import factory

from .models import Topic

from subjects.factories import RandomSubjectFactory
from users.factories import RandomUserFactory

class RandomTopicFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Topic

    name = factory.Sequence(lambda n: "Tópico %03d" % n)
    subject = factory.SubFactory(RandomSubjectFactory, professor=(RandomUserFactory.create_batch(1, is_staff=False)), students=(RandomUserFactory.create_batch(10, is_staff=False)))
    repository = False