""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from django.test import TestCase
from django.urls import reverse, resolve

from users.views import login, logout, DeleteView, CreateView, UpdateView, ChangePassView, SearchView, UpdateProfile, \
    SupportView, RegisterUser, ForgotPassword, PasswordResetConfirmView, UsersListView, Profile


class UserTest(TestCase):

    def test_login_url_resolves(self):
        url = reverse('users:login')
        self.assertEquals(resolve(url).func, login)

    def test_logout_url_resolves(self):
        url = reverse("users:logout")
        self.assertEquals(resolve(url).func, logout)

    def test_singup_url_resolves(self):
        url = reverse("users:signup")
        self.assertEquals(resolve(url).func.view_class, RegisterUser)

    def test_forgot_password_url_resolves(self):
        url = reverse("users:forgot_pass")
        self.assertEquals(resolve(url).func.view_class, ForgotPassword)

    def test_reset_password_confirm_url_resolves(self):
        url = reverse("users:reset_password_confirm")
        self.assertEquals(resolve(url).func.view_class, PasswordResetConfirmView)

    def test_manage_users_url_resolves(self):
        url = reverse("users:manage")
        self.assertEquals(resolve(url).func.view_class, UsersListView)

    def test_create_view_url_resolves(self):
        url = reverse("users:create")
        self.assertEquals(resolve(url).func.view_class, CreateView)

    def test_update_view_url_resolves(self):
        url = reverse("users:update")
        self.assertEquals(resolve(url).func.view_class, UpdateView)

    def test_delete_view_url_resolves(self):
        url = reverse("users:delete")
        self.assertEquals(resolve(url).func.view_class, DeleteView)

    def test_search_url_resolves(self):
        url = reverse("users:search")
        self.assertEquals(resolve(url).func.view_class, SearchView)

    def test_profile_url_resolves(self):
        url = reverse("users:profile")
        self.assertEquals(resolve(url).func.view_class, Profile)

    def test_edit_profile_url_resolves(self):
        url = reverse("users:edit_profile")
        self.assertEquals(resolve(url).func.view_class, UpdateProfile)

    def test_change_pass_url_resolves(self):
        url = reverse("users:change_pass")
        self.assertEquals(resolve(url).func.view_class, ChangePassView)

    def test_remove_account_url_resolves(self):
        url = reverse("users:remove_acc")
        self.assertEquals(resolve(url).func.view_class, DeleteView)

    def test_select_support_url_resolves(self):
        url = reverse("users:support_select")
        self.assertEquals(resolve(url).func.view_class, SupportView)
