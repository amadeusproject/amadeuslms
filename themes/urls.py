from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.IndexView.as_view(), name = 'manage'),
	url(r'^basic_elements$', views.BasicElementsSettings.as_view(), name = 'basic'),
	url(r'^css_selector$', views.CSSStyleSettings.as_view(), name = 'css'),
]