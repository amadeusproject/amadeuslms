from django.db import models

class Exam(models.Model):
	name = models.CharField(_('Name'), max_length = 100)
	beginDate = models.DateTimeField(_('Start Date'), auto_now_add = True)
	endDate = models.DateTimeField(_('Date of last update'), auto_now=True)

    class Meta:

        verbose_name = _('Exam')
        verbose_name_plural = _('Exams')

    def __str__(self):
        return str(self.name) + str("/") + str(self.topic)

class Answer(models.Model):
    answer = models.CharField(_("Answer"), max_length = 200)
    order = models.PositiveSmallIntegerField(_("Order"))
    exam = models.ForeignKey(Poll, verbose_name = _('Answers'), related_name='answers')

    class Meta:
        ordering = ('order',)
        verbose_name = _('Answer')
        verbose_name_plural = _('Answers')

    def __str__(self):
        return str(self.answer) + str("/") + str(self.poll)
