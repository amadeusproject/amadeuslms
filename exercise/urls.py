from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^create_exercise/(?P<slug>[\w_-]+)/$', views.CreateExercise.as_view(), name='create_exercise'),
    url(r'^delete_exercise/(?P<slug>[\w_-]+)/$', views.DeleteExercise.as_view(), name='delete_exercise'),
    url(r'^update_exercise/(?P<slug>[\w_-]+)/$', views.UpdateExercise.as_view(), name='update_exercise'),
    url(r'^render-exercise/(?P<id>[0-9]+)/$', views.render_exercise, name='render_exercise'),
]
