""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""
from django.test import TestCase
from django.urls import reverse, resolve

from categories.views import IndexView, CreateCategory, DeleteCategory, UpdateCategory, category_view_log

class TestUrls(TestCase):
    def test_create_view_resolves(self):
        url = reverse('categories:create')
        self.assertEquals(resolve(url).func.view_class, CreateCategory)

    def test_update_view_resolves(self):
        url = reverse('categories:update', kwargs={"slug": "test"})
        self.assertEquals(resolve(url).func.view_class, UpdateCategory)

    def test_replicate_view_resolves(self):
        url = reverse('categories:replicate', kwargs={"slug": "test"})
        self.assertEquals(resolve(url).func.view_class, CreateCategory)

    def test_delete_view_resolves(self):
        url = reverse('categories:delete', kwargs={"slug": "test"})
        self.assertEquals(resolve(url).func.view_class, DeleteCategory)

    def test_list_view_resolves(self):
        url = reverse('categories:index')
        self.assertEquals(resolve(url).func.view_class, IndexView)

    def test_view_log_resolves(self):
        url = reverse('categories:view_log', kwargs={"category": "test"})
        self.assertEquals(resolve(url).func, category_view_log)