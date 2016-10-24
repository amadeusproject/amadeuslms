from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^$', views.UsersListView.as_view(), name='manage'),
	url(r'^create/$', views.Create.as_view(), name='create'),
	url(r'^edit/(?P<username>[\w_-]+)/$', views.Update.as_view(), name='update'),
	url(r'^view/(?P<username>[\w_-]+)/$', views.View.as_view(), name='view'),
	url(r'^delete/(?P<username>[\w_-]+)/$', views.delete, name='delete'),
	url(r'^profile/$', views.Profile.as_view(), name='profile'),
	#
	url(r'^profile/update/$', views.UpdateProfile.as_view(), name='update_profile'),
            url(r'^profile/change_password/$', views.Change_password.as_view(), name='change_password'),
	url(r'^profile/delete/$', views.DeleteUser.as_view(), name='delete_profile'),
]
