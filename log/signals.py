from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Log

@receiver(post_save, sender=Log)
def index_log(sender, instance, **kwargs):
    instance.indexing()