""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r"^create/(?P<slug>[\w_-]+)/$", views.CreateView.as_view(), name="create"),
    url(r"^update/(?P<topic_slug>[\w_-]+)/(?P<slug>[\w_-]+)/$", views.UpdateView.as_view(), name="update"),
    url(r"^delete/(?P<slug>[\w_-]+)/$", views.DeleteView.as_view(), name="delete"),
    url(r"^view/(?P<slug>[\w_-]+)/$", views.DetailView.as_view(), name="view"),
    url(r"^submit_material/(?P<deliver>[\w_-]+)/$", views.StudentMaterialCreate.as_view(), name="submit_material"),
    url(r"^evaluate/(?P<deliver>[\w_-]+)/$", views.TeacherEvaluate.as_view(), name="evaluate"),
    url(r"^evaluate_update/(?P<deliver>[\w_-]+)/(?P<pk>[\w_-]+)/$", views.TeacherUpdateEvaluation.as_view(), name="evaluate_update"),
]