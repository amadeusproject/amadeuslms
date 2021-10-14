""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""
from django.test import TestCase
from django.urls import reverse, resolve

from topics.views import CreateView, UpdateView, DeleteView, topic_view_log, update_order, update_resource_order

class TestUrls(TestCase):
    def test_create_view_resolves(self):
        url = reverse('topics:create', kwargs={"slug": "test"})
        self.assertEquals(resolve(url).func.view_class, CreateView)

    def test_update_view_resolves(self):
        url = reverse('topics:update', kwargs={"sub_slug": "test", "slug": "test"})
        self.assertEquals(resolve(url).func.view_class, UpdateView)

    def test_delete_view_resolves(self):
        url = reverse('topics:delete', kwargs={"slug": "test"})
        self.assertEquals(resolve(url).func.view_class, DeleteView)
    
    def test_view_log_resolves(self):
        url = reverse('topics:view_log', kwargs={"topic": "test"})
        self.assertEquals(resolve(url).func, topic_view_log)

    def test_update_order_resolves(self):
        url = reverse('topics:update_order')
        self.assertEquals(resolve(url).func, update_order)

    def test_update_resource_order_resolve(self):
        url = reverse('topics:update_resource_order')
        self.assertEquals(resolve(url).func, update_resource_order)