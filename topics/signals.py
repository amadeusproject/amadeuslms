from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Resource

@receiver(post_save, sender=Resource)
def index_resource(sender, instance, **kwargs):
    instance.indexing()