from django.db import models
from django.db.models import Q

from autoslug.fields import AutoSlugField

from django.utils.translation import ugettext_lazy as _

from users.models import User

from django.core.exceptions import ValidationError

from categories.models import Category
import datetime

class Tag(models.Model):
    name = models.CharField( _("Name"), unique = True,max_length= 200, blank = True)
    
    def __str__(self):
        return self.name

class Subject(models.Model):

    name = models.CharField( _("Name"), unique = True,max_length= 200)
    slug = AutoSlugField(_("Slug"),populate_from='name',unique=True)

    description_brief = models.TextField(_("simpler_description"), blank=True)
    description = models.TextField(_("description"), blank= True)
    visible = models.BooleanField(_("visible"))

    init_date = models.DateField(_('Begin of Subject Date'))
    end_date = models.DateField(_('End of Subject Date'))

    tags = models.ManyToManyField(Tag, verbose_name='tags', blank=True)

    create_date = models.DateTimeField(_('Creation Date'), auto_now_add = True)
    update_date = models.DateTimeField(_('Date of last update'), auto_now=True)

    subscribe_begin = models.DateField(_('Begin Subscribe'))
    subscribe_end = models.DateField(_('End Subscribe'))

    professor = models.ManyToManyField(User, related_name="professors", blank=True)
    students = models.ManyToManyField(User,verbose_name=_('Students'), related_name='subject_student', blank = True)

    category = models.ForeignKey(Category, related_name="subject_category", null=True)

    max_upload_size = models.IntegerField(_("Maximum upload size"), default=1024, null=True)
    
    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"
        ordering = ['name']

    def __str__(self):
        return self.name
    
    def get_participants(self):
        data = User.objects.filter(
            Q(is_staff = True) | Q(subject_student__slug = self.slug) |
            Q(professors__slug = self.slug) |
            Q(coordinators__subject_category__slug = self.slug)
            ).distinct()

        return data