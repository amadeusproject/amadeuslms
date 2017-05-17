from django.conf.urls import url, include
from . import views


urlpatterns = [
	url(r'^general/$', views.GeneralView.as_view(), name='view_general'),
	url(r'^categories/$', views.CategoryView.as_view(), name='view_categories'),
]