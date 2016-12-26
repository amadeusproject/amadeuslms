from django.db import models

from autoslug.fields import AutoSlugField

from django.utils.translation import ugettext_lazy as _

from users.models import User

from categories.models import Category

class Subject(models.Model):

    name = models.CharField( _("Name"), unique = True,max_length= 200)
    slug = AutoSlugField(_("Slug"),populate_from='name',unique=True)

    description_brief = models.CharField(_("simpler_description"), max_length= 100)
    description = models.CharField(_("description"), max_length = 300)
    visible = models.BooleanField(_("visible"))

    init_date = models.DateField(_('Begin of Subject Date'))
    end_date = models.DateField(_('End of Subject Date'))

    create_date = models.DateTimeField(_('Creation Date'), auto_now_add = True)
    update_date = models.DateTimeField(_('Date of last update'), auto_now=True)

    professor = models.ForeignKey(User, related_name="professor")
    students = models.ManyToManyField(User,verbose_name=_('Students'), related_name='subject_student', blank = True)

    category = models.ForeignKey(Category, related_name="subject_category")

    max_upload_size = models.IntegerField(_("Maximum upload size"))
    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"

    def __str__(self):
        pass
    


