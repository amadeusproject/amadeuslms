from courses.models import Topic
from decimal import Decimal
from django.db import models
from django.utils.translation import ugettext_lazy as _
from users.models import User
from core.models import MimeType

"""
    Function to return the path where the file should be saved
"""

    
def file_path(instance, filename):
    return '/'.join([instance.topic.subject.course.slug, instance.topic.subject.slug, instance.topic.slug, filename])


"""
It represents the Exercises inside topic.
"""


class Exercise(models.Model):
    name_exercise = models.CharField(_('Name'), max_length=100)
    description = models.TextField(_('Description'), blank=True)
    init_date = models.DateField(_('Begin of Subject Date'))
    end_date = models.DateField(_('End of Subject Date'))
    grade = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'), null=True)
    topic = models.ForeignKey(Topic, verbose_name=_('Topic'), related_name='exercises')
    professors = models.ManyToManyField(User, verbose_name=_('Professors'), related_name='professors_exercise', blank=True)
    students = models.ManyToManyField(User, verbose_name=_('Students'), related_name='subject_exercise', blank = True)
    file = models.FileField(upload_to=file_path)
    file_type = models.ForeignKey(MimeType, verbose_name=_('Type file'), related_name='exercise_type')

    def __str__(self):
        return self.name_exercise