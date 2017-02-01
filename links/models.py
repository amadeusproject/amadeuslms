from django.db import models
from django.utils.translation import ugettext_lazy as _
from autoslug.fields import AutoSlugField

import datetime
from topics.models import Topic, Resource
from users.models import User
from django.utils import timezone
# Create your models here.
class Link(Resource):
    link_url = models.URLField(verbose_name = _("Link_URL"))
    
   
    class Meta:
        verbose_name = "Link"
        verbose_name_plural = "Links"

    def __str__(self):
        return self.name

    def access_link(self):
        return 'links:view'

    def update_link(self):
        return 'links:update'

    def delete_link(self):
        return 'links:delete'
    