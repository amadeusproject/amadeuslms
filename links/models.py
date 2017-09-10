from django.db import models
from django.utils.translation import ugettext_lazy as _
from autoslug.fields import AutoSlugField

import datetime
from topics.models import Topic, Resource
from users.models import User
from django.utils import timezone
from django.core.urlresolvers import reverse_lazy

# Create your models here.
class Link(Resource):
    link_url = models.CharField( _("Link_URL"),max_length=250 )


    class Meta:
        verbose_name = "Link"
        verbose_name_plural = "Links"

    def __str__(self):
        return self.name

    def access_link(self):
        return reverse_lazy('links:view', kwargs = {'slug': self.slug})

    def update_link(self):
        return 'links:update'

    def delete_link(self):
        return 'links:delete'

    def delete_message(self):
        return _('Are you sure you want delete the Website link')
