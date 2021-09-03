""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""
from django.test import TestCase
from django.urls import reverse, resolve

from mural.views import *

class TestUrls(TestCase):
    def test_general_page_view_resolves(self):
        url = reverse('mural:manage_general')
        self.assertEquals(resolve(url).func.view_class, GeneralIndex)

    def test_category_page_view_resolves(self):
        url = reverse('mural:manage_category')
        self.assertEquals(resolve(url).func.view_class, CategoryIndex)
    
    def test_subject_page_view_resolves(self):
        url = reverse('mural:manage_subject')
        self.assertEquals(resolve(url).func.view_class, SubjectIndex)

    def test_general_create_view_resolves(self):
        url = reverse('mural:create_general')
        self.assertEquals(resolve(url).func.view_class, GeneralCreate)

    def test_category_create_view_resolves(self):
        url = reverse('mural:create_category', kwargs={"slug": "teste"})
        self.assertEquals(resolve(url).func.view_class, CategoryCreate)
    
    def test_subject_create_view_resolves(self):
        url = reverse('mural:create_subject', kwargs={"slug": "teste"})
        self.assertEquals(resolve(url).func.view_class, SubjectCreate)
    
    def test_resource_create_view_resolves(self):
        url = reverse('mural:create_resource', kwargs={"slug": "teste", "rslug": "test"})
        self.assertEquals(resolve(url).func.view_class, ResourceCreate)

    def test_general_update_view_resolves(self):
        url = reverse('mural:update_general', kwargs={"pk": "1"})
        self.assertEquals(resolve(url).func.view_class, GeneralUpdate)
    
    def test_category_update_view_resolves(self):
        url = reverse('mural:update_category', kwargs={"pk": "1"})
        self.assertEquals(resolve(url).func.view_class, CategoryUpdate)
    
    def test_subject_update_view_resolves(self):
        url = reverse('mural:update_subject', kwargs={"pk": "1"})
        self.assertEquals(resolve(url).func.view_class, SubjectUpdate)

    def test_general_delete_view_resolves(self):
        url = reverse('mural:delete_general', kwargs={"pk": "1"})
        self.assertEquals(resolve(url).func.view_class, GeneralDelete)
    
    def test_category_delete_view_resolves(self):
        url = reverse('mural:delete_category', kwargs={"pk": "1"})
        self.assertEquals(resolve(url).func.view_class, CategoryDelete)
    
    def test_subject_delete_view_resolves(self):
        url = reverse('mural:delete_subject', kwargs={"pk": "1"})
        self.assertEquals(resolve(url).func.view_class, SubjectDelete)

    def test_subject_view_resolves(self):
        url = reverse('mural:subject_view', kwargs={"slug": "teste"})
        self.assertEquals(resolve(url).func.view_class, SubjectView)
    
    def test_resource_view_resolves(self):
        url = reverse('mural:resource_view', kwargs={"slug": "teste"})
        self.assertEquals(resolve(url).func.view_class, ResourceView)

    def test_category_load_view_resolves(self):
        url = reverse('mural:load_category', args={"teste"})
        self.assertEquals(resolve(url).func, load_category_posts)
    
    def test_subject_load_view_resolves(self):
        url = reverse('mural:load_subject', args={"teste"})
        self.assertEquals(resolve(url).func, load_subject_posts)
    
    def test_category_view_log_resolves(self):
        url = reverse('mural:view_log_cat', kwargs={"category": "teste"})
        self.assertEquals(resolve(url).func, mural_category_log)
    
    def test_subject_view_log_resolves(self):
        url = reverse('mural:view_log_sub', kwargs={"subject": "teste"})
        self.assertEquals(resolve(url).func, mural_subject_log)

    def test_favorite_resolves(self):
        url = reverse('mural:favorite', args={"true"})
        self.assertEquals(resolve(url).func, favorite)
    
    def test_deleted_resolves(self):
        url = reverse('mural:deleted_post')
        self.assertEquals(resolve(url).func, deleted_post)

    def test_comment_create_view_resolves(self):
        url = reverse('mural:create_comment', kwargs={"post": "teste"})
        self.assertEquals(resolve(url).func.view_class, CommentCreate)
    
    def test_comment_update_view_resolves(self):
        url = reverse('mural:update_comment', kwargs={"pk": "1"})
        self.assertEquals(resolve(url).func.view_class, CommentUpdate)
    
    def test_comment_delete_view_resolves(self):
        url = reverse('mural:delete_comment', kwargs={"pk": "1"})
        self.assertEquals(resolve(url).func.view_class, CommentDelete)

    def test_deleted_comment_resolves(self):
        url = reverse('mural:deleted_comment')
        self.assertEquals(resolve(url).func, deleted_comment)

    def test_render_comment_resolves(self):
        url = reverse('mural:render_comment', args={"a", "b"})
        self.assertEquals(resolve(url).func, render_comment)
    
    def test_render_post_resolves(self):
        url = reverse('mural:render_post', args={"a", "b", "c"})
        self.assertEquals(resolve(url).func, render_post)

    def test_load_comments_resolves(self):
        url = reverse('mural:load_comments', args={"a", "b"})
        self.assertEquals(resolve(url).func, load_comments)

    def test_suggest_users_resolves(self):
        url = reverse('mural:suggest_users')
        self.assertEquals(resolve(url).func, suggest_users)