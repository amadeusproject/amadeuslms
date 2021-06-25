""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""
from django.test import TestCase

from django.utils.translation import ugettext_lazy as _

from categories.forms import CategoryForm

from categories.models import Category

class TestForm(TestCase):
    def create_category(self):
        return Category.objects.create(name="Categoria Teste")

    def test_form_same_name(self):
        category = self.create_category()

        form_data = {"name": category.name}
        form = CategoryForm(data=form_data)

        self.assertEquals(form.errors["name"], [_('There is another category with this name, try another one.')])

    def test_form_update_not_trigger_same_name(self):
        category = self.create_category()

        form_data = {"name": category.name, "description": "teste de descrição"}
        form = CategoryForm(instance=category, data=form_data)

        self.assertTrue(form.is_valid())