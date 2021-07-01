""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""
from django.test import TestCase
from django.urls import reverse, resolve

from subjects.views import *

class TestUrls(TestCase):
    def test_home_view_resolves(self):
        url = reverse("subjects:home")
        self.assertEquals(resolve(url).func.view_class, HomeView)

    def test_index_view_resolves(self):
        url = reverse("subjects:index")
        self.assertEquals(resolve(url).func.view_class, IndexView)

    def test_index_option_view_resolves(self):
        url = reverse("subjects:index", kwargs={"option": "test"})
        self.assertEquals(resolve(url).func.view_class, IndexView)

    def test_index_category_view_resolves(self):
        url = reverse("subjects:cat_view", kwargs={"slug": "test"})
        self.assertEquals(resolve(url).func.view_class, IndexView)

    def test_create_view_resolves(self):
        url = reverse("subjects:create", kwargs={"slug": "test"})
        self.assertEquals(resolve(url).func.view_class, SubjectCreateView)

    def test_update_view_resolves(self):
        url = reverse("subjects:update", kwargs={"slug": "test"})
        self.assertEquals(resolve(url).func.view_class, SubjectUpdateView)

    def test_delete_view_resolves(self):
        url = reverse("subjects:delete", kwargs={"slug": "test"})
        self.assertEquals(resolve(url).func.view_class, SubjectDeleteView)

    def test_replicate_view_resolves(self):
        url = reverse("subjects:replicate", kwargs={"subject_slug": "test"})
        self.assertEquals(resolve(url).func.view_class, SubjectCreateView)

    def test_backup_view_resolves(self):
        url = reverse("subjects:backup", kwargs={"slug": "test"})
        self.assertEquals(resolve(url).func.view_class, Backup)

    def test_restore_view_resolves(self):
        url = reverse("subjects:restore", kwargs={"slug": "test"})
        self.assertEquals(resolve(url).func.view_class, Restore)

    def test_detail_view_resolves(self):
        url = reverse("subjects:view", kwargs={"slug": "test"})
        self.assertEquals(resolve(url).func.view_class, SubjectDetailView)

    def test_topic_detail_view_resolves(self):
        url = reverse("subjects:topic_view", kwargs={"slug": "test", "topic_slug": "test"})
        self.assertEquals(resolve(url).func.view_class, SubjectDetailView)

    def test_subscribe_view_resolves(self):
        url = reverse("subjects:subscribe", kwargs={"slug": "test"})
        self.assertEquals(resolve(url).func.view_class, SubjectSubscribeView)

    def test_search_view_resolves(self):
        url = reverse("subjects:search")
        self.assertEquals(resolve(url).func.view_class, SubjectSearchView)

    def test_option_view_resolves(self):
        url = reverse("subjects:search", kwargs={"option": "test"})
        self.assertEquals(resolve(url).func.view_class, SubjectSearchView)

    def test_list_view_resolves(self):
        url = reverse("subjects:load_view", kwargs={"slug": "test"})
        self.assertEquals(resolve(url).func.view_class, GetSubjectList)

    def test_logs_view_resolves(self):
        url = reverse("subjects:view_log", kwargs={"subject": "test"})
        self.assertEquals(resolve(url).func, subject_view_log)

    def test_participants_view_resolves(self):
        url = reverse("subjects:get_participants", kwargs={"subject": "test"})
        self.assertEquals(resolve(url).func, get_participants)

    def test_visualization_view_resolves(self):
        url = reverse("subjects:toggle_student_visualization", kwargs={"subject": "test"})
        self.assertEquals(resolve(url).func, toggleVisualization)

    def test_do_backup_view_resolves(self):
        url = reverse("subjects:do_backup", kwargs={"subject": "test"})
        self.assertEquals(resolve(url).func, realize_backup)

    def test_do_restore_view_resolves(self):
        url = reverse("subjects:do_restore", kwargs={"subject": "test"})
        self.assertEquals(resolve(url).func, realize_restore)