from django.db import models
from subject.models import Tag

from topics.models import Topic
from users.models import User
# Create your models here.
class Link(models.Model):
	name = models.CharField( _("Name"), unique = True,max_length= 200)
    slug = AutoSlugField(_("Slug"),populate_from='name',unique=True)

    description_brief = models.TextField(_("simpler_description"), blank=True)
    description = models.TextField(_("description"), blank= True)

    link_url = models.URLField(verbose_name = _("Link_URL"))

    tags = models.ManyToManyField(Tag, verbose_name='tags', blank=True, null=True)
    visible = models.BooleanField(_('Visible'), default = True)
    all_students = models.BooleanField(_('all_students'), default= False)
    students = models.ManyToManyField(User,verbose_name=_('Students'), related_name='students', blank = True)
    topic = models.ForeignKey(Topic, verbose_name='topic')
    initial_view = models.BooleanField(_('Initial View'), default = False)
    initia_view_date = models.DateField(_('Initial View Date'), required= False)
    class Meta:
        verbose_name = "Link"
        verbose_name_plural = "Links"

    def __str__(self):
        pass
    