from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.ListNewsView.as_view(), name='manage_news'),

]
