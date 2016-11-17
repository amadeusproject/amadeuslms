from django.db import models
from courses.models import Topic
from django.utils.translation import ugettext_lazy as _
from users.models import User

"""
    Function to return the path where the file should be saved
"""

    
def file_path(instance, filename):
    return '/'.join([instance.topic.subject.course.slug, instance.topic.subject.slug, instance.topic.slug, filename])


"""
It represents the Exercises inside topic.
"""


class Exercise(models.Model):
    topic = models.ForeignKey(Topic, verbose_name=_('Topic'), related_name='exercises')
    professors = models.ManyToManyField(User, verbose_name=_('Professors'), related_name='professors_exercise')
    students = models.ManyToManyField(User, verbose_name=_('Students'), related_name='subject_exercise', blank = True)
    file = models.FileField(upload_to='uploads/%Y/%m/%d')
    name = models.CharField(max_length=100)
