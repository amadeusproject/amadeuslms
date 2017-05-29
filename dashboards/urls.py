from django.conf.urls import url, include
from . import views


urlpatterns = [
	url(r'^general/$', views.GeneralView.as_view(), name='view_general'),
	url(r'^general/log/$', views.LogView.as_view(), name='view_general_log'),
	url(r'^categories/$', views.CategoryView.as_view(), name='view_categories'),
	url(r'^get_log_data/$', views.load_log_data, name='load_log_data')
]