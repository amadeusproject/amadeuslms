from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^', include('subscriptions.urls', namespace = 'subscription')),
    url(r'^', include('courses.urls', namespace = 'course')),
    url(r'^cursos/participantes/$', views.participantes_curso, name='participantes_curso'),
    url(r'^cursos/avaliacoes/$', views.avaliacao_curso, name='avaliacao_curso'),
    url(r'^usuarios/', include('users.urls', namespace = 'users')),
    url(r'^enviar_email/$', views.email, name='send_mail'),
    url(r'^perfil/$', views.profile, name='profile'),
    url(r'^perfil/editar/$', views.edit_profile, name='editar_profile'),
    url(r'^perfil/alterar_senha/$', views.reset_pass, name='alterar_senha'),
    url(r'^perfil/colegas/$', views.colegas, name='colegas'),
    url(r'^configuracoes/$', views.configuracoes, name='config'),
    url(r'^mobile/$', views.mobile, name='mobile'),
    url(r'^tarefas/$', views.tarefas, name='tarefas'),
    url(r'^online/$', views.users_online, name='online'),
    url(r'^busca/$', views.search, name='search'),
]