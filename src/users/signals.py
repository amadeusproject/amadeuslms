from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Account, User


@receiver(post_save, sender=Account)
def create_user_profile(sender, instance, created, **kwargs):
  if created:
    User.objects.get_or_create(account=instance)
