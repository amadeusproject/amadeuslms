from django.utils.translation import ugettext_lazy as _
from django.db import models
from autoslug.fields import AutoSlugField
from users.models import User
from core.models import Resource
from courses.models import Activity

class Poll(Activity):

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

class AnswersStudent(models.Model):
    status = models.BooleanField(_("Answered"), default=False)
    poll = models.ForeignKey(Poll, verbose_name = _('Poll'), related_name='answers_stundet')
    answer = models.ManyToManyField(Answer,verbose_name = _('Answers Students'), related_name='answers_stundet')
    student = models.ForeignKey(User, verbose_name = _('Student'), related_name='answers_stundent')
    answered_in = models.DateTimeField(_("Answered Date"),auto_now=True)

    class Meta:
        verbose_name = _('Answer Stundent')
        verbose_name_plural = _('Answers Student')

    def __str__(self):
        return str(self.student) + str("/") + str(self.poll)
