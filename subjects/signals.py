from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Tag

@receiver(post_save, sender=Tag)
def index_tag(sender, instance, **kwargs):
    instance.indexing()