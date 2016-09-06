from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^users/$', views.UsersListView.as_view(), name='manage'),
	url(r'^users/create/$', views.Create.as_view(), name='create'),
	url(r'^user/edit/(?P<username>[\w_-]+)/$', views.Update.as_view(), name='update'),
	url(r'^user/data/(?P<username>[\w_-]+)/$', views.View.as_view(), name='view'),
	url(r'^profile/$', views.Profile.as_view(), name='profile'),
	url(r'^profile/edit/(?P<username>[\w_-]+)/$', views.EditProfile.as_view(), name='edit_profile'),
]
