from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^', include('courses.urls', namespace = 'course')),
    url(r'^', include('users.urls', namespace = 'users')),
]