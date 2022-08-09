""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""
from django.contrib import auth
from django.contrib.auth import authenticate, login

from oauth2_provider.models import AccessToken
from users.models import User

class ExternalLoginMiddleware(object):
    def __init__(self, get_response = None):
        self.get_response = get_response

    def process_request(self, request):
        if request.GET and str(auth.get_user(request)) == 'AnonymousUser':
            token = request.GET.get("token", "")

            oauth_user = AccessToken.objects.filter(token=token).last()

            if oauth_user is not None:
                user = User.objects.filter(id=oauth_user.user.id).first()

                if user is not None:
                    login(request, user)
