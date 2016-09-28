from django.utils.translation import ugettext_lazy as _
from django.db import models

from autoslug.fields import AutoSlugField

from courses.models import Activity
from users.models import User

"""
It's one kind of activity available for a Topic.
It works like a 'topic' of forum, which users can post to it and answer posts of it.
"""
class Forum(Activity):
	description = models.TextField(_('Description'), blank = True)
	modification_date = models.DateTimeField(_('Modification Date'), auto_now = True)
	create_date = models.DateTimeField(_('Create Date'), auto_now_add = True)

	class Meta:
		verbose_name = _('Forum')
		verbose_name_plural = _('Foruns')
		app_label ='forum'

	def __str__(self):
		return self.name

"""
It represents a post made in a forum (topic)
"""
class Post(models.Model):
	user = models.ForeignKey(User, verbose_name = _('Autor'))
	message = models.TextField(_('Post message'), blank = False)
	modification_date = models.DateTimeField(_('Modification Date'), auto_now = True)
	post_date = models.DateTimeField(_('Post Date'), auto_now_add = True)
	forum = models.ForeignKey(Forum, verbose_name = _('Forum'))

	class Meta:
		verbose_name = _('Post')
		verbose_name_plural = _('Posts')
		app_label ='forum'

	def __str__(self):
		return ''.join([self.user.name, " / ", str(self.post_date)])

"""
It represents an answer to a forum's post
"""
class PostAnswer(models.Model):
	user = models.ForeignKey(User, verbose_name = _('Autor'))
	post = models.ForeignKey(Post, verbose_name = _('Post'))
	message = models.TextField(_('Answer message'), blank = False)
	modification_date = models.DateTimeField(_('Modification Date'), auto_now = True)
	answer_date = models.DateTimeField(_('Answer Date'), auto_now_add = True)

	class Meta:
		verbose_name = _('Post Answer')
		verbose_name_plural = _('Post Answers')
		app_label ='forum'

	def __str__(self):
		return ''.join([self.user.name, " / ", str(self.answer_date)])	