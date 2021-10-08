"""
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco

Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS

O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.

Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.

Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

import factory

from datetime import datetime, timedelta

from .models import Subject

from categories.factories import RandomCategoryFactory
from users.factories import RandomUserFactory

class RandomSubjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Subject

    name = factory.Sequence(lambda n: "Assunto %03d" % n)
    category = factory.SubFactory(RandomCategoryFactory, coordinators=(RandomUserFactory.create(is_staff=False),))
    init_date = factory.LazyAttribute(lambda a: a.subscribe_end + timedelta(days=1))
    end_date = factory.LazyAttribute(lambda a: a.init_date + timedelta(days=30))
    subscribe_begin = factory.LazyFunction(datetime.now)
    subscribe_end = factory.LazyAttribute(lambda a: a.subscribe_begin + timedelta(days=7))
    visible = True

    @factory.post_generation
    def professor(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for prof in extracted:
                prof.save()
                self.professor.add(prof)

    @factory.post_generation
    def students(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for student in extracted:
                student.save()
                self.students.add(student)