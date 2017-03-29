from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.GeneralIndex.as_view(), name='manage_general'),
	url(r'^categories/$', views.CategoryIndex.as_view(), name='manage_category'),
	url(r'^subjects/$', views.SubjectIndex.as_view(), name='manage_subject'),
	url(r'^participants/$', views.GeneralParticipants.as_view(), name='participants_general'),
	url(r'^category/talks/(?P<category>[\w_-]+)/$', views.CategoryTalks.as_view(), name='category_talks'),
	url(r'^category/participants/(?P<category>[\w_-]+)/$', views.CategoryParticipants.as_view(), name='participants_category'),
	url(r'^subject/talks/(?P<subject>[\w_-]+)/$', views.SubjectTalks.as_view(), name='subject_talks'),
	url(r'^subject/participants/(?P<subject>[\w_-]+)/$', views.SubjectParticipants.as_view(), name='participants_subject'),
	url(r'^render_message/([\w_-]+)/([\w_-]+)/([\w_-]+)/([\w_-]+)/([\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/$', views.render_message, name='render_message'),
	url(r'^favorite/([\w_-]+)/$', views.favorite, name='favorite'),
	url(r'^load_messages/([\w_-]+)/$', views.load_messages, name='load_messages'),
	url(r'^talk/(?P<email>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/$', views.GetTalk.as_view(), name = 'talk'),
	url(r'^send_message/(?P<email>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/(?P<talk_id>[\w_-]+)/(?P<space>[\w_-]+)/(?P<space_type>[\w_-]+)/$', views.SendMessage.as_view(), name = 'create'),
	url(r'^participant/profile/(?P<email>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/$', views.ParticipantProfile.as_view(), name = 'profile'),
]