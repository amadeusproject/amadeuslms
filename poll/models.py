from django.utils.translation import ugettext_lazy as _
from django.db import models
from autoslug.fields import AutoSlugField
from users.models import User
from core.models import Resource
from courses.models import Activity

class Poll(Activity):
    question = models.CharField(_('Question'), max_length = 300)

    class Meta:
		#ordering = ('create_date','name')
        verbose_name = _('Poll')
        verbose_name_plural = _('Polls')

    def __str__(self):
        return str(self.name) + str("/") + str(self.topic)

class Answer(models.Model):
    answer = models.CharField(_("Answer"), max_length = 200)
    order = models.PositiveSmallIntegerField(_("Order"))
    poll = models.ForeignKey(Poll, verbose_name = _('Answers'), related_name='answers')

    class Meta:
        ordering = ('order',)
        verbose_name = _('Answer')
        verbose_name_plural = _('Answers')

    def __str__(self):
        return str(self.answer) + str("/") + str(self.poll)
