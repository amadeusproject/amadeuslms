from django.utils.translation import ugettext_lazy as _
from django.db import models
from autoslug.fields import AutoSlugField
from users.models import User
from core.models import Resource
from courses.models import Activity

class Exam(Activity):
    begin_date = models.DateField(_('Begin of Course Date'), blank=True)
    begin_exam = models.DateField(_('Begin of Exam'), blank = True)
    end_exam = models.DateField(_('End of Exam'), blank = True)
    exibe = models.BooleanField(_('Exibe?'), default=False)

    class Meta:
        verbose_name = _('Exam')
        verbose_name_plural = _('Exams')

        def __str__(self):
            return str(self.name) + str("/") + str(self.topic)


class Answer(models.Model):
    answer = models.CharField(_("Answer"), max_length = 300)
    order = models.PositiveSmallIntegerField(_("Order"))
    exam = models.ForeignKey(Exam, verbose_name = _('Answers'), related_name='answers')

    class Meta:
        ordering = ('order',)
        verbose_name = _('Answer')
        verbose_name_plural = _('Answers')

    def __str__(self):
        return str(self.answer) + str("/") + str(self.exam)

class AnswersStudent(models.Model):
    status = models.BooleanField(_("Answered"), default=False)
    exam = models.ForeignKey(Exam, verbose_name = _('Exam'), related_name='student_exam')
    answer = models.ManyToManyField(Answer,verbose_name = _('Answers Students'), related_name='student_answer')
    student = models.ForeignKey(User, verbose_name = _('Student'), related_name='student')
    answered_in = models.DateTimeField(_("Answered Date"),auto_now=True)

    class Meta:
        verbose_name = _('Answer Stundent')
        verbose_name_plural = _('Answers Student')

    def __str__(self):
        return str(self.student) + str("/") + str(self.exam)

class Question(models.Model):
    exam = models.ForeignKey(Exam, verbose_name=_('Exam'), related_name='question_exam')
    statement = models.TextField(_("Statement"), blank=False)

class Alternative(models.Model):
    question = models.ForeignKey(Question, verbose_name=_("Question"), related_name="alternative_question")
    statement = models.TextField(_("Statement"), blank=False)
    answer = models.BooleanField(_("answer"), default=False)